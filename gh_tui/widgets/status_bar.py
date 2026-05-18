from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static


class StatusBar(Static):
    """Bottom bar with ASCII separators and minimal styling."""

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: #1a1a1a;
        color: #707070;
        padding: 0 2;
        border-top: solid #2a2a2a;
        content-align: left middle;
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
            parts.append(f"[#d4a373]{message}[/#d4a373]")
        
        if repo:
            loc = f"{repo}/{path}" if path else repo
            parts.append(f"[#a0a0a0]{loc}[/#a0a0a0]")
        
        if stale:
            parts.append("[dim]⊖ cache[/dim]")
        
        if rate_remaining is not None and rate_limit is not None:
            color = "#d4a373" if rate_remaining < 100 else "#707070"
            parts.append(f"[{color}]⚡{rate_remaining}/{rate_limit}[/{color}]")
        
        # ASCII separators
        sep = " │ "
        self.update(sep.join(parts) if parts else "gh-tui")
