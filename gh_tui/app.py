from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import App

from gh_tui.api.client import GitHubClient
from gh_tui.config import CONFIG_FILE, AppConfig
from gh_tui.screens.auth import AuthScreen
from gh_tui.screens.repo import RepoScreen
from gh_tui.screens.search import SearchScreen


class GhTuiApp(App):
  """gh-tui main application."""

  TITLE = "gh-tui"
  CSS_PATH = Path(__file__).parent / "styles" / "app.tcss"

  BINDINGS = [
    ("q", "quit", "Quit"),
    ("ctrl+c", "quit", "Quit"),
    ("slash", "search", "Search"),
  ]

  def __init__(
    self,
    config: AppConfig | None = None,
    initial_repo: str | None = None,
  ) -> None:
    super().__init__()
    self.config = config or AppConfig.load()
    self._initial_repo = initial_repo or self.config.default_repo
    self.client = GitHubClient(
      token=self.config.github_token,
      ttl_seconds=self.config.cache_ttl_seconds,
    )

  def on_mount(self) -> None:
    self._repo_screen = RepoScreen(self.client, repo_name=self._initial_repo)
    self.push_screen(self._repo_screen)
    if not CONFIG_FILE.exists():
      self._prompt_auth()
    else:
      self._maybe_notify_public_mode()

  @work
  async def _prompt_auth(self) -> None:
    result = await self.push_screen_wait(AuthScreen())
    if result:
      self.config = AppConfig.load()
      self.client = GitHubClient(
        token=self.config.github_token,
        ttl_seconds=self.config.cache_ttl_seconds,
      )
    self._repo_screen._client = self.client
    self._repo_screen.after_auth()
    self._maybe_notify_public_mode()

  def _maybe_notify_public_mode(self) -> None:
    if not self.config.is_authenticated:
      self.notify(
        "Public-only mode — add a token in ~/.config/gh-tui/config.toml for private repos",
        timeout=8,
      )

  def push_search(self) -> None:
    def on_result(full_name: str | None) -> None:
      if full_name:
        self._repo_screen.load_repo(full_name)

    self.push_screen(SearchScreen(self.client), on_result)

  def action_search(self) -> None:
    self.push_search()
