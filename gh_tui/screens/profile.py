from __future__ import annotations

import webbrowser

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import ListItem, ListView, Static

from gh_tui.api.client import GitHubAPIError, GitHubClient
from gh_tui.api.models import UserProfile
from gh_tui.widgets.info_panel import InfoPanel
from gh_tui.widgets.status_bar import StatusBar


class ProfileScreen(Screen):
  """User/Org profile screen with repo list."""

  BINDINGS = [
    ("escape,h", "go_back", "Back"),
    ("b", "open_browser", "Browser"),
    ("r", "refresh", "Refresh"),
    ("slash", "search", "Search"),
    ("tab", "cycle_focus", "Next panel"),
  ]

  def __init__(
    self,
    client: GitHubClient,
    username: str,
  ) -> None:
    super().__init__()
    self._client = client
    self._username = username
    self._user: UserProfile | None = None
    self._browser_url: str | None = None
    self._stale = False

  def compose(self) -> ComposeResult:
    yield Static(
      "[bold]gh-tui[/bold]  ·  [dim]/[/dim] search  [dim]q[/dim] quit",
      id="header",
    )
    yield Static("", id="banner")
    with Horizontal(id="profile-layout"):
      yield ListView(id="repo-list")
      yield InfoPanel(id="profile-info")
    yield StatusBar(id="status-bar")

  def on_mount(self) -> None:
    self.load_user(self._username)

  @work(exclusive=True)
  async def load_user(self, login: str, *, refresh: bool = False) -> None:
    self._username = login
    self.query_one("#banner", Static).update(login)
    self.query_one("#status-bar", StatusBar).update_status(
      repo=login, message=f"Loading {login}…"
    )
    try:
      self._user = await self._client.get_user(login, refresh=refresh)
      repos = await self._client.get_user_repos(login, refresh=refresh)
    except GitHubAPIError as exc:
      self._show_error(str(exc), exc.status_code)
      return
    except Exception as exc:
      self._show_error(f"Failed to load profile: {exc}", None)
      return

    self._stale = self._client.last_response_stale
    self._browser_url = self._user.html_url
    self.query_one("#profile-info", InfoPanel).show_user(self._user, stale=self._stale)
    self._populate_repo_list(repos)
    self.query_one("#repo-list", ListView).focus()
    self._update_status()

  def _populate_repo_list(self, repos) -> None:
    list_view = self.query_one("#repo-list", ListView)
    list_view.clear()
    if not repos:
      list_view.append(ListItem(Static("[dim]No public repos[/dim]")))
      return
    for repo in repos:
      desc = (repo.description or "")[:60]
      lang = f"  [dim]{repo.language}[/dim]" if repo.language else ""
      label = f"[bold #e0e0e0]{repo.full_name}[/#e0e0e0]  ★ {repo.stars}{lang}"
      if desc:
        label += f"\n[dim]{desc}[/dim]"
      row = ListItem(Static(label))
      row.data = {"full_name": repo.full_name}
      list_view.append(row)

  @on(ListView.Selected, "#repo-list")
  def on_repo_selected(self, event: ListView.Selected) -> None:
    item = event.item
    if item is None:
      return
    data = getattr(item, "data", None) or {}
    full_name = data.get("full_name")
    if full_name:
      self.dismiss(full_name)

  def action_go_back(self) -> None:
    self.dismiss(None)

  def action_open_browser(self) -> None:
    url = self._browser_url
    if url:
      webbrowser.open(url)
    else:
      self.notify("Nothing to open", severity="warning")

  def action_refresh(self) -> None:
    self.load_user(self._username, refresh=True)

  def action_search(self) -> None:
    self.app.push_search()

  def action_cycle_focus(self) -> None:
    order = [
      self.query_one("#repo-list", ListView),
      self.query_one("#profile-info", InfoPanel),
    ]
    visible = [w for w in order if w.display]
    if not visible:
      return
    try:
      idx = visible.index(self.focused)
      visible[(idx + 1) % len(visible)].focus()
    except ValueError:
      visible[0].focus()

  def _show_error(self, message: str, status_code: int | None) -> None:
    if status_code == 404:
      message = "User or organization not found"
    elif status_code == 403:
      message = "Rate limited or forbidden. Check your token."
    self.query_one("#profile-info", InfoPanel).update(f"[red]{message}[/red]")
    self._update_status(message=message)

  def _update_status(self, message: str | None = None) -> None:
    rl = self._client.rate_limit
    self.query_one("#status-bar", StatusBar).update_status(
      repo=self._username,
      rate_remaining=rl.remaining,
      rate_limit=rl.limit,
      message=message,
      stale=self._stale,
    )
