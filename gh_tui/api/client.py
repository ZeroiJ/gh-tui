from __future__ import annotations

from dataclasses import dataclass

import httpx

from gh_tui.api import rest
from gh_tui.api.models import ContentFile, Repository, SearchResult, TreeEntry
from gh_tui.cache.store import CacheStore


@dataclass
class RateLimitInfo:
  limit: int
  remaining: int
  reset_at: int | None = None


class GitHubAPIError(Exception):
  def __init__(self, message: str, status_code: int | None = None) -> None:
    super().__init__(message)
    self.status_code = status_code


class GitHubClient:
  BASE_URL = "https://api.github.com"

  def __init__(
    self,
    token: str | None = None,
    cache: CacheStore | None = None,
    ttl_seconds: int = 600,
  ) -> None:
    self._token = token
    self._cache = cache or CacheStore()
    self._ttl = ttl_seconds
    self.rate_limit = RateLimitInfo(limit=60, remaining=60)
    self.last_response_stale = False

  def _headers(self) -> dict[str, str]:
    headers = {
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "gh-tui",
    }
    if self._token:
      headers["Authorization"] = f"Bearer {self._token}"
    return headers

  def _update_rate_limit(self, response: httpx.Response) -> None:
    try:
      self.rate_limit = RateLimitInfo(
        limit=int(response.headers.get("x-ratelimit-limit", self.rate_limit.limit)),
        remaining=int(
          response.headers.get("x-ratelimit-remaining", self.rate_limit.remaining)
        ),
        reset_at=int(response.headers["x-ratelimit-reset"])
        if response.headers.get("x-ratelimit-reset")
        else None,
      )
    except (TypeError, ValueError):
      pass

  async def _request(
    self,
    method: str,
    path: str,
    *,
    params: dict | None = None,
    use_cache: bool = True,
    cache_key: str | None = None,
  ) -> dict | list:
    key = cache_key or f"{method}:{path}:{params}"
    self.last_response_stale = False
    if use_cache:
      cached, is_stale = self._cache.get(key)
      if cached is not None and not is_stale:
        return cached
      if cached is not None and is_stale:
        self.last_response_stale = True

    url = path if path.startswith("http") else f"{self.BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
      try:
        response = await client.request(
          method, url, headers=self._headers(), params=params
        )
      except httpx.RequestError as exc:
        if use_cache:
          cached, is_stale = self._cache.get(key)
          if cached is not None:
            self.last_response_stale = is_stale or True
            return cached
        raise GitHubAPIError(f"Network error: {exc}") from exc

    self._update_rate_limit(response)

    if response.status_code == 404:
      raise GitHubAPIError("Not found", status_code=404)
    if response.status_code == 403:
      msg = "Rate limited or forbidden. Check your token."
      try:
        body = response.json()
        if "message" in body:
          msg = body["message"]
      except Exception:
        pass
      raise GitHubAPIError(msg, status_code=403)
    if response.status_code >= 400:
      raise GitHubAPIError(
        f"API error ({response.status_code})", status_code=response.status_code
      )

    data = response.json()
    if use_cache:
      self._cache.set(key, data, ttl_seconds=self._ttl)
    return data

  async def search_repos(self, query: str) -> list[SearchResult]:
    data = await self._request(
      "GET",
      "/search/repositories",
      params={"q": query, "per_page": 20, "sort": "stars"},
      cache_key=f"search:{query}",
    )
    return rest.parse_search_results(data)

  async def get_repo(self, full_name: str, *, refresh: bool = False) -> Repository:
    if refresh:
      self._cache.delete(f"repo:{full_name}")
    data = await self._request(
      "GET",
      f"/repos/{full_name}",
      cache_key=f"repo:{full_name}",
      use_cache=not refresh,
    )
    return rest.parse_repo(data)

  async def get_readme(self, full_name: str, *, refresh: bool = False) -> str:
    key = f"readme:{full_name}"
    if refresh:
      self._cache.delete(key)
    data = await self._request(
      "GET",
      f"/repos/{full_name}/readme",
      cache_key=key,
      use_cache=not refresh,
    )
    return rest.decode_content(data)

  async def get_contents(
    self, full_name: str, path: str = "", *, refresh: bool = False
  ) -> list[TreeEntry]:
    key = f"contents:{full_name}:{path}"
    if refresh:
      self._cache.delete(key)
    endpoint = f"/repos/{full_name}/contents/{path}" if path else f"/repos/{full_name}/contents"
    data = await self._request("GET", endpoint, cache_key=key, use_cache=not refresh)
    return rest.parse_contents(data)

  async def get_file_content(
    self, full_name: str, path: str, *, refresh: bool = False
  ) -> ContentFile:
    key = f"file:{full_name}:{path}"
    if refresh:
      self._cache.delete(key)
    data = await self._request(
      "GET",
      f"/repos/{full_name}/contents/{path}",
      cache_key=key,
      use_cache=not refresh,
    )
    return rest.parse_file_content(data)
