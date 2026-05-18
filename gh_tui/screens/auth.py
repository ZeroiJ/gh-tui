from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from gh_tui.config import AppConfig


class AuthScreen(ModalScreen[bool]):
  """First-run prompt for GitHub personal access token."""

  DEFAULT_CSS = """
  AuthScreen {
    align: center middle;
  }
  #auth-dialog {
    width: 60;
    max-width: 90%;
    border: thick $accent;
    background: $surface;
    padding: 1 2;
  }
  #auth-input {
    margin: 1 0;
  }
  .auth-buttons {
    height: auto;
    layout: horizontal;
    align: right middle;
  }
  """

  def compose(self) -> ComposeResult:
    with Vertical(id="auth-dialog"):
      yield Static(
        "[bold]GitHub authentication[/bold]\n\n"
        "Enter a classic Personal Access Token for private repos "
        "and higher rate limits.\n\n"
        "[dim]Create one at: github.com → Settings → Developer settings "
        "→ Personal access tokens[/dim]\n\n"
        "Leave empty to continue in public-only mode (60 req/hr)."
      )
      yield Input(password=True, placeholder="ghp_…", id="auth-input")
      with Horizontal(classes="auth-buttons"):
        yield Button("Save token", variant="primary", id="auth-save")
        yield Button("Skip (public only)", id="auth-skip")

  def on_mount(self) -> None:
    self.query_one("#auth-input", Input).focus()

  @on(Button.Pressed, "#auth-save")
  def on_save(self) -> None:
    token = self.query_one("#auth-input", Input).value.strip()
    config = AppConfig.load()
    config.github_token = token or None
    config.save()
    # Empty save = same as skip (public-only)
    self.dismiss(bool(token))

  @on(Button.Pressed, "#auth-skip")
  def on_skip(self) -> None:
    config = AppConfig.load()
    config.github_token = None
    config.save()
    self.dismiss(False)
