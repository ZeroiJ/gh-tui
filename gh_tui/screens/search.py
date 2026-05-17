from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, ListItem, ListView, Static

from gh_tui.api.client import GitHubAPIError, GitHubClient
from gh_tui.api.models import SearchResult


class SearchScreen(ModalScreen[str | None]):
  """Modal overlay to search GitHub repositories."""

  BINDINGS = [
    ("escape", "dismiss", "Close"),
  ]

  DEFAULT_CSS = """
  SearchScreen {
    align: center middle;
  }
  #search-dialog {
    width: 70;
    max-width: 90%;
    height: auto;
    max-height: 80%;
    border: thick $accent;
    background: $surface;
    padding: 1 2;
  }
  #search-input {
    margin-bottom: 1;
  }
  #search-results {
    height: 16;
    max-height: 50vh;
    border: solid $primary-background;
  }
  """

  def __init__(self, client: GitHubClient) -> None:
    super().__init__()
    self._client = client
    self._results: list[SearchResult] = []

  def compose(self) -> ComposeResult:
    with Vertical(id="search-dialog"):
      yield Static("[bold]Search repositories[/bold]  (Enter to open, Esc to close)")
      yield Input(placeholder="owner/repo or keywords…", id="search-input")
      yield ListView(id="search-results")
      yield Static("[dim]Type to search GitHub[/dim]", id="search-hint")

  def on_mount(self) -> None:
    self.query_one("#search-input", Input).focus()

  @on(Input.Changed, "#search-input")
  def on_input_changed(self, event: Input.Changed) -> None:
    query = event.value.strip()
    if len(query) < 2:
      self._clear_results()
      return
    self._search(query)

  @work(exclusive=True)
  async def _search(self, query: str) -> None:
    hint = self.query_one("#search-hint", Static)
    hint.update("[dim]Searching…[/dim]")
    try:
      self._results = await self._client.search_repos(query)
    except GitHubAPIError as exc:
      hint.update(f"[red]{exc}[/red]")
      self._clear_results()
      return

    list_view = self.query_one("#search-results", ListView)
    list_view.clear()
    if not self._results:
      hint.update("[dim]No results[/dim]")
      return
    hint.update(f"[dim]{len(self._results)} results[/dim]")
    for item in self._results:
      desc = (item.description or "")[:60]
      label = f"[bold]{item.full_name}[/bold]  ★ {item.stars}"
      if desc:
        label += f"\n[dim]{desc}[/dim]"
      list_view.append(ListItem(Static(label), id=item.full_name))

  def _clear_results(self) -> None:
    self.query_one("#search-results", ListView).clear()
    self._results = []

  @on(ListView.Selected, "#search-results")
  def on_result_selected(self, event: ListView.Selected) -> None:
    item = event.item
    if item is None:
      return
    self.dismiss(item.id)

  def action_dismiss(self) -> None:
    self.dismiss(None)
