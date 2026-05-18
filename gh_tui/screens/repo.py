from __future__ import annotations

import webbrowser
from enum import Enum

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from gh_tui.api.client import GitHubAPIError, GitHubClient
from gh_tui.api.models import ContentFile, Repository
from gh_tui.widgets.code_view import CodeView
from gh_tui.widgets.file_tree import FileTree
from gh_tui.widgets.info_panel import InfoPanel
from gh_tui.widgets.markdown_view import MarkdownView
from gh_tui.widgets.status_bar import StatusBar


class ViewMode(Enum):
  README = "readme"
  FILE = "file"


class RepoScreen(Screen):
  """Main repository browser screen."""

  BINDINGS = [
    ("escape,h", "show_readme", "README"),
    ("b", "open_browser", "Browser"),
    ("r", "refresh", "Refresh"),
    ("slash", "search", "Search"),
    ("tab", "cycle_focus", "Next panel"),
  ]

  def __init__(
    self,
    client: GitHubClient,
    repo_name: str | None = None,
    name: str | None = None,
  ) -> None:
    super().__init__(name=name)
    self._client = client
    self._repo_name = repo_name
    self._repo: Repository | None = None
    self._mode = ViewMode.README
    self._current_path: str | None = None
    self._browser_url: str | None = None
    self._stale = False

  def compose(self) -> ComposeResult:
    yield Static(
      "[bold]gh-tui[/bold]  ·  [dim]/[/dim] search  [dim]q[/dim] quit",
      id="header",
    )
    yield Static("", id="banner")
    with Horizontal(id="main-layout"):
      yield FileTree("Files", id="file-tree")
      yield MarkdownView(id="markdown-view")
      yield CodeView(id="code-view")
      yield InfoPanel(id="info-panel")
    yield StatusBar(id="status-bar")

  def on_mount(self) -> None:
    self.query_one("#code-view", CodeView).display = False

  def on_ready(self) -> None:
    if self._repo_name:
      self.load_repo(self._repo_name)
    else:
      self._show_welcome()
    self.query_one("#file-tree", FileTree).focus()

  def after_auth(self) -> None:
    """Restore UI after the auth modal closes."""
    if not self._repo_name:
      self._show_welcome()
    self.query_one("#file-tree", FileTree).focus()

  def _show_welcome(self) -> None:
    self.query_one("#code-view", CodeView).display = False
    self.query_one("#markdown-view", MarkdownView).display = True
    self.query_one("#info-panel", InfoPanel).show_placeholder()
    self.query_one("#markdown-view", MarkdownView).show_message(
      "[bold #d4a373]██████╗ ██╗  ██╗     ████████╗██╗   ██╗██╗[/bold #d4a373]\n"
      "[bold #d4a373]██╔════╝ ██║  ██║     ╚══██╔══╝██║   ██║██║[/bold #d4a373]\n"
      "[bold #d4a373]██║  ███╗███████║        ██║   ██║   ██║██║[/bold #d4a373]\n"
      "[bold #d4a373]██║   ██║██╔══██║        ██║   ██║   ██║██║[/bold #d4a373]\n"
      "[bold #d4a373]╚██████╔╝██║  ██║        ██║   ╚██████╔╝██║[/bold #d4a373]\n"
      "[bold #d4a373]╚═════╝ ╚═╝  ╚═╝        ╚═╝    ╚═════╝ ╚═╝[/bold #d4a373]\n\n"
      "[bold]Welcome to gh-tui[/bold]\n\n"
      "Press [bold]/[/bold] then type e.g. [bold]textualize/rich[/bold]\n"
      "or run: [bold]gh-tui textualize/rich[/bold]\n\n"
      "[dim]Do not include 'gh-tui' in the search box.[/dim]"
    )
    self._update_status(message="Press / to search")

  @work(exclusive=True)
  async def load_repo(self, full_name: str, *, refresh: bool = False) -> None:
    from gh_tui.utils.repo_name import normalize_repo_query

    full_name = normalize_repo_query(full_name)
    self._repo_name = full_name
    self._show_loading(f"Loading {full_name}…")
    try:
      self._repo = await self._client.get_repo(full_name, refresh=refresh)
      readme = await self._client.get_readme(full_name, refresh=refresh)
      entries = await self._client.get_contents(full_name, refresh=refresh)
    except GitHubAPIError as exc:
      self._show_error(str(exc), exc.status_code)
      return
    except Exception as exc:
      self._show_error(f"Failed to load repo: {exc}", None)
      return

    self._stale = self._client.last_response_stale
    self._browser_url = self._repo.html_url
    self.query_one("#file-tree", FileTree).load_root(entries)
    self.query_one("#info-panel", InfoPanel).show_repo(self._repo, stale=self._stale)
    self._show_readme_view(readme)
    self._mode = ViewMode.README
    self._current_path = None
    self.query_one("#banner", Static).update(full_name)
    self._update_status()

  @on(FileTree.EntrySelected)
  def on_tree_entry(self, event: FileTree.EntrySelected) -> None:
    if not self._repo_name:
      return
    if event.entry_type == "dir":
      self._load_directory(event.path)
    else:
      self._load_file(event.path)

  @work(exclusive=True)
  async def _load_directory(self, path: str) -> None:
    if not self._repo_name:
      return
    try:
      entries = await self._client.get_contents(self._repo_name, path)
    except GitHubAPIError as exc:
      self.notify(str(exc), severity="error")
      return
    self.query_one("#file-tree", FileTree).add_children(path, entries)

  @work(exclusive=True)
  async def _load_file(self, path: str) -> None:
    if not self._repo_name:
      return
    self._show_loading(f"Loading {path}…")
    try:
      file: ContentFile = await self._client.get_file_content(self._repo_name, path)
    except GitHubAPIError as exc:
      self._show_error(str(exc), exc.status_code)
      return

    self._mode = ViewMode.FILE
    self._current_path = path
    self._browser_url = file.html_url or (
      f"https://github.com/{self._repo_name}/blob/"
      f"{self._repo.default_branch if self._repo else 'main'}/{path}"
    )
    md = self.query_one("#markdown-view", MarkdownView)
    code = self.query_one("#code-view", CodeView)
    md.display = False
    code.display = True
    lang = self._repo.language if self._repo else None
    code.show_file(path, file.content, language=lang, is_binary=file.is_binary)
    self._update_status()

  def _show_readme_view(self, content: str) -> None:
    md = self.query_one("#markdown-view", MarkdownView)
    code = self.query_one("#code-view", CodeView)
    md.display = True
    code.display = False
    md.show_markdown(content, title="README")

  def action_show_readme(self) -> None:
    if not self._repo_name or self._mode == ViewMode.README:
      return
    self._mode = ViewMode.README
    self._current_path = None
    if self._repo:
      self._browser_url = self._repo.html_url
    self.run_worker(self._reload_readme(), exclusive=True)

  @work(exclusive=True)
  async def _reload_readme(self) -> None:
    if not self._repo_name:
      return
    try:
      readme = await self._client.get_readme(self._repo_name)
    except GitHubAPIError as exc:
      self.notify(str(exc), severity="error")
      return
    self._show_readme_view(readme)
    self._update_status()

  def action_refresh(self) -> None:
    if self._repo_name:
      self.load_repo(self._repo_name, refresh=True)

  def action_open_browser(self) -> None:
    url = self._browser_url
    if url:
      webbrowser.open(url)
    else:
      self.notify("Nothing to open", severity="warning")

  def action_search(self) -> None:
    self.app.push_search()

  def action_cycle_focus(self) -> None:
    order = [
      self.query_one("#file-tree", FileTree),
      self.query_one("#markdown-view", MarkdownView),
      self.query_one("#code-view", CodeView),
      self.query_one("#info-panel", InfoPanel),
    ]
    visible = [w for w in order if w.display]
    if not visible:
      return
    try:
      idx = visible.index(self.focused)
      visible[(idx + 1) % len(visible)].focus()
    except ValueError:
      visible[0].focus()

  def _show_loading(self, message: str) -> None:
    self.query_one("#banner", Static).update(message)
    self.query_one("#markdown-view", MarkdownView).display = True
    self.query_one("#code-view", CodeView).display = False
    self.query_one("#markdown-view", MarkdownView).show_message(message)
    self._update_status(message=message)

  def _show_error(self, message: str, status_code: int | None) -> None:
    self.query_one("#banner", Static).update("")
    if status_code == 404:
      message = "Repository not found"
    elif status_code == 403:
      message = "Rate limited or forbidden. Check your token."
    elif "network" in message.lower():
      message = "Network error — check your connection"
    self.query_one("#markdown-view", MarkdownView).display = True
    self.query_one("#code-view", CodeView).display = False
    self.query_one("#markdown-view", MarkdownView).show_message(f"[red]{message}[/red]")
    self._update_status(message=message)

  def _update_status(self, message: str | None = None) -> None:
    rl = self._client.rate_limit
    self.query_one("#status-bar", StatusBar).update_status(
      repo=self._repo_name,
      path=self._current_path,
      rate_remaining=rl.remaining,
      rate_limit=rl.limit,
      message=message,
      stale=self._stale,
    )

  def refresh_rate_limit(self) -> None:
    self._update_status()
