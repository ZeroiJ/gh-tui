from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static

from gh_tui.api.models import Repository
from gh_tui.utils.formatters import format_count, format_relative_date


class InfoPanel(Static):
    """Right panel with repository metadata - clean ASCII styling."""

    DEFAULT_CSS = """
    InfoPanel {
        width: 28;
        min-width: 24;
        height: 100%;
        border: none;
        border-left: solid #2a2a2a;
        background: #161616;
        padding: 1 2;
        color: #a0a0a0;
        overflow-y: auto;
    }
    
    InfoPanel:focus {
        border-left: solid #d4a373;
        background: #181818;
    }
    """

    def show_repo(self, repo: Repository, *, stale: bool = False) -> None:
        lines = [
            f"[bold #e0e0e0]{repo.full_name}[/bold #e0e0e0]",
            "",
        ]
        if repo.description:
            lines.extend([repo.description, ""])
        if stale:
            lines.append("[dim ⚠] cached data[/dim ⚠]")
            lines.append("")
        
        # ASCII box for stats
        lines.append("┌────────────────────┐")
        lines.append(f"│ * {format_count(repo.stars):>15} │")
        lines.append(f"│ ⎕ {format_count(repo.forks):>15} │")
        lines.append(f"│ ◙ {format_count(repo.watchers):>14} │")
        lines.append(f"│ # {repo.open_issues:>15} │")
        lines.append("└────────────────────┘")
        lines.append("")
        
        if repo.language:
            lines.append(f"lang: [#d4a373]{repo.language}[/#d4a373]")
        if repo.license_name:
            lines.append(f"lic:  {repo.license_name}")
        if repo.is_private:
            lines.append("[dim]private repo[/dim]")
        lines.extend(["", f"upd {format_relative_date(repo.updated_at)}"])
        self.update("\n".join(lines))

    def show_placeholder(self) -> None:
        self.update(
            "[dim]── gh-tui ──[/dim]\n\n"
            "[dim]│ search  /[/dim]\n"
            "[dim]│ browser b[/dim]\n"
            "[dim]│ refresh r[/dim]\n"
            "[dim]│ quit    q[/dim]\n"
            "[dim]└────────[/dim]"
        )
