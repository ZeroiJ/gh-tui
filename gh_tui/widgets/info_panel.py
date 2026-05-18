from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static

from gh_tui.api.models import Repository, UserProfile
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

    def show_user(self, user: UserProfile, *, stale: bool = False) -> None:
        lines = []
        login = getattr(user, "login", "")
        name = getattr(user, "name", None)
        bio = getattr(user, "bio", None)
        location = getattr(user, "location", None)
        company = getattr(user, "company", None)
        created_at = getattr(user, "created_at", None)
        typ = getattr(user, "type", None)

        # Top line: login in bold with color #e0e0e0
        if login:
            lines.append(f"[bold #e0e0e0]{login}[/]")
        else:
            lines.append("[bold #e0e0e0]Unknown[/]")

        # Display name if different
        if name and name != login:
            lines.append(f"[#e0e0e0]{name}[/]")

        # Bio
        if bio:
            lines.append(bio)

        # Location and company
        if location:
            lines.append(f"[#707070]Location: {location}[/]")
        if company:
            lines.append(f"[#707070]Company: {company}[/]")

        # ASCII stats box
        followers = format_count(getattr(user, "followers", 0) or 0)
        following = format_count(getattr(user, "following", 0) or 0)
        public_repos = format_count(getattr(user, "public_repos", 0) or 0)

        lines.extend([
            "┌────────────────────┐",
            f"│ ◙{followers:>14} │",
            f"│ ★{following:>15} │",
            f"│ ⎕{public_repos:>15} │",
            "└────────────────────┘",
        ])

        # Type and joined date
        if typ:
            lines.append(f"[#707070]{typ}[/]")
        if created_at:
            lines.append(f"[#707070]Joined {format_relative_date(created_at)}[/]")

        if stale:
            lines.append("[#707070]Stale data[/]")

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
