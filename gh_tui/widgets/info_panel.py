from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static

from gh_tui.api.models import Repository
from gh_tui.utils.formatters import format_count, format_relative_date


class InfoPanel(Static):
  """Right panel with repository metadata."""

  DEFAULT_CSS = """
  InfoPanel {
    width: 1fr;
    min-width: 24;
    max-width: 36;
    border: solid $primary-background;
    padding: 1 2;
    overflow-y: auto;
  }
  """

  def show_repo(self, repo: Repository, *, stale: bool = False) -> None:
    lines = [
      f"[bold]{repo.full_name}[/bold]",
      "",
    ]
    if repo.description:
      lines.extend([repo.description, ""])
    if stale:
      lines.append("[yellow]⚠ Showing cached data[/yellow]")
      lines.append("")
    lines.extend(
      [
        f"★ [bold]{format_count(repo.stars)}[/bold] stars",
        f"⑂ [bold]{format_count(repo.forks)}[/bold] forks",
        f"◎ {format_count(repo.watchers)} watchers",
        f"⚑ {repo.open_issues} open issues",
        "",
      ]
    )
    if repo.language:
      lines.append(f"Language: [cyan]{repo.language}[/cyan]")
    if repo.license_name:
      lines.append(f"License: {repo.license_name}")
    if repo.is_private:
      lines.append("[dim]Private repository[/dim]")
    lines.extend(["", f"Updated {format_relative_date(repo.updated_at)}"])
    self.update("\n".join(lines))

  def show_placeholder(self) -> None:
    self.update(
      "[dim]Select a repository\nwith / to search[/dim]\n\n"
      "Keys:\n"
      "  /  search\n"
      "  b  browser\n"
      "  r  refresh\n"
      "  q  quit"
    )
