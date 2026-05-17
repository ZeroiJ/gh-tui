from __future__ import annotations

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


CONFIG_DIR = Path.home() / ".config" / "gh-tui"
CONFIG_FILE = CONFIG_DIR / "config.toml"


class AppConfig(BaseSettings):
  model_config = SettingsConfigDict(
    env_prefix="GH_TUI_",
    env_file_encoding="utf-8",
  )

  github_token: str | None = Field(default=None, alias="token")
  cache_ttl_seconds: int = 600
  default_repo: str | None = None

  @classmethod
  def load(cls) -> AppConfig:
    if CONFIG_FILE.exists():
      return cls._from_toml(CONFIG_FILE)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    return cls(github_token=token)

  @classmethod
  def _from_toml(cls, path: Path) -> AppConfig:
    import tomllib

    with path.open("rb") as f:
      data = tomllib.load(f)
    github = data.get("github", {})
    cache = data.get("cache", {})
    return cls(
      github_token=github.get("token"),
      cache_ttl_seconds=cache.get("ttl_seconds", 600),
      default_repo=data.get("default_repo"),
    )

  def save(self) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
      "[github]",
      f'token = "{self.github_token or ""}"',
      "",
      "[cache]",
      f"ttl_seconds = {self.cache_ttl_seconds}",
      "",
    ]
    if self.default_repo:
      lines.insert(0, f'default_repo = "{self.default_repo}"\n')
    CONFIG_FILE.write_text("\n".join(lines))
    if self.github_token:
      CONFIG_FILE.chmod(0o600)

  @property
  def is_authenticated(self) -> bool:
    return bool(self.github_token)
