from __future__ import annotations

import asyncio

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, ListItem, ListView, Static

from gh_tui.api.client import GitHubAPIError, GitHubClient
from gh_tui.api.models import SearchResult
from gh_tui.utils.repo_name import looks_like_repo_name, normalize_repo_query

SEARCH_DEBOUNCE_SECONDS = 0.4


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
    border: solid #3a3a3a;
    background: #1a1a1a;
    padding: 1 2;
  }
  #search-input {
    margin-bottom: 1;
  }
  #search-results {
    height: 16;
    max-height: 50vh;
    border: none;
    border-top: solid #2a2a2a;
    background: #141414;
  }
  """

  def __init__(self, client: GitHubClient) -> None:
    super().__init__()
    self._client = client
    self._results: list[SearchResult] = []
    self._search_query: str | None = None

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
    self._search_query = query
    self._do_search()

  def _do_search(self) -> None:
    self.run_worker(self._debounced_search(), exclusive=True)

  async def _debounced_search(self) -> None:
    await asyncio.sleep(SEARCH_DEBOUNCE_SECONDS)
    query = self._search_query
    if query and self.is_mounted:
      await self._search(query)

  async def _search(self, query: str) -> None:
    query = normalize_repo_query(query)
    hint = self.query_one("#search-hint", Static)

    if looks_like_repo_name(query):
      hint.update(f"[dim]Opening {query}…[/dim]")
      self.dismiss(query)
      return

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
      row = ListItem(Static(label))
      row.data = {"full_name": item.full_name}
      list_view.append(row)

  def _clear_results(self) -> None:
    self.query_one("#search-results", ListView).clear()
    self._results = []

  @on(ListView.Selected, "#search-results")
  def on_result_selected(self, event: ListView.Selected) -> None:
    item = event.item
    if item is None:
      return
    data = getattr(item, "data", None) or {}
    full_name = data.get("full_name")
    if full_name:
      self.dismiss(full_name)

  def action_dismiss(self) -> None:
    self.dismiss(None)
