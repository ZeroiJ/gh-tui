from __future__ import annotations

import base64
import binascii

from gh_tui.api.models import ContentFile, Repository, SearchResult, TreeEntry

BINARY_EXTENSIONS = {
  ".png",
  ".jpg",
  ".jpeg",
  ".gif",
  ".ico",
  ".woff",
  ".woff2",
  ".ttf",
  ".eot",
  ".zip",
  ".gz",
  ".tar",
  ".pdf",
  ".exe",
  ".dll",
  ".so",
  ".dylib",
  ".bin",
  ".wasm",
  ".mp3",
  ".mp4",
  ".avi",
  ".mov",
  ".pyc",
  ".class",
  ".o",
  ".a",
}


def parse_repo(data: dict) -> Repository:
  license_info = data.get("license") or {}
  return Repository(
    full_name=data["full_name"],
    description=data.get("description"),
    stars=data.get("stargazers_count", 0),
    forks=data.get("forks_count", 0),
    watchers=data.get("subscribers_count", 0),
    language=data.get("language"),
    license_name=license_info.get("spdx_id") or license_info.get("name"),
    html_url=data["html_url"],
    default_branch=data.get("default_branch", "main"),
    updated_at=data.get("updated_at", ""),
    open_issues=data.get("open_issues_count", 0),
    is_private=data.get("private", False),
  )


def parse_search_results(data: dict) -> list[SearchResult]:
  items = data.get("items", [])
  return [
    SearchResult(
      full_name=item["full_name"],
      description=item.get("description"),
      stars=item.get("stargazers_count", 0),
      language=item.get("language"),
      html_url=item["html_url"],
    )
    for item in items
  ]


def parse_contents(data: dict | list) -> list[TreeEntry]:
  if isinstance(data, dict):
    data = [data]
  entries: list[TreeEntry] = []
  for item in data:
    entry_type = "dir" if item.get("type") == "dir" else "file"
    entries.append(
      TreeEntry(
        name=item["name"],
        path=item["path"],
        entry_type=entry_type,
        size=item.get("size"),
        sha=item.get("sha"),
      )
    )
  entries.sort(key=lambda e: (e.entry_type != "dir", e.name.lower()))
  return entries


def decode_content(data: dict) -> str:
  content = data.get("content", "")
  encoding = data.get("encoding", "base64")
  if encoding == "base64":
    try:
      return base64.b64decode(content).decode("utf-8")
    except (UnicodeDecodeError, binascii.Error):
      return "[Binary or undecodable content]"
  return content


def parse_file_content(data: dict) -> ContentFile:
  path = data["path"]
  name = data["name"]
  html_url = data.get("html_url", "")
  size = data.get("size", 0)
  ext = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
  is_binary = ext in BINARY_EXTENSIONS or data.get("encoding") != "base64"

  if data.get("type") == "dir":
    return ContentFile(
      path=path,
      name=name,
      content="",
      encoding="",
      size=size,
      html_url=html_url,
      is_binary=False,
    )

  if is_binary:
    return ContentFile(
      path=path,
      name=name,
      content="",
      encoding=data.get("encoding", ""),
      size=size,
      html_url=html_url,
      is_binary=True,
    )

  text = decode_content(data)
  return ContentFile(
    path=path,
    name=name,
    content=text,
    encoding=data.get("encoding", "base64"),
    size=size,
    html_url=html_url,
    is_binary=False,
  )
