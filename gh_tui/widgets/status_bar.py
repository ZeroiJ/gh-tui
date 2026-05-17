from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static


class StatusBar(Static):
  """Bottom bar showing repo context and API rate limit."""

  DEFAULT_CSS = """
  StatusBar {
    dock: bottom;
    height: 1;
    background: $surface-darken-1;
    color: $text-muted;
    padding: 0 1;
  }
  """

  def update_status(
    self,
    *,
    repo: str | None = None,
    path: str | None = None,
    rate_remaining: int | None = None,
    rate_limit: int | None = None,
    message: str | None = None,
    stale: bool = False,
  ) -> None:
    parts: list[str] = []
    if message:
      parts.append(message)
    if repo:
      loc = f"{repo}/{path}" if path else repo
      parts.append(loc)
    if stale:
      parts.append("⚠ stale cache")
    if rate_remaining is not None and rate_limit is not None:
      parts.append(f"API {rate_remaining}/{rate_limit}")
    self.update("  │  ".join(parts) if parts else "gh-tui")
