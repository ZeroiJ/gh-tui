from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Markdown, Static


class MarkdownView(Static):
  """Scrollable markdown renderer for README content."""

  DEFAULT_CSS = """
  MarkdownView {
    width: 1fr;
    min-width: 30;
    border: solid $primary-background;
    padding: 1 2;
    overflow-y: auto;
  }
  """

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self._markdown: Markdown | None = None

  def show_markdown(self, content: str, *, title: str = "README") -> None:
    self.remove_children()
    header = Static(f"[bold]{title}[/bold]\n")
    header.can_focus = False
    self.mount(header)
    try:
      md = Markdown(content)
      self._markdown = md
      self.mount(md)
    except Exception:
      self._markdown = None
      self.mount(Static(content))

  def show_message(self, message: str) -> None:
    self.remove_children()
    self.mount(Static(message))
