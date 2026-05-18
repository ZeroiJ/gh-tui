from __future__ import annotations

from textual.containers import VerticalScroll
from textual.widgets import Markdown, Static


class MarkdownView(VerticalScroll):
  """Scrollable markdown renderer for README content."""

  DEFAULT_CSS = """
  MarkdownView {
    width: 1fr;
    min-width: 24;
    height: 100%;
    border: solid $primary-background;
    padding: 1 2;
  }
  """

  def show_markdown(self, content: str, *, title: str = "README") -> None:
    self.remove_children()
    self.mount(Static(f"[bold]{title}[/bold]\n"))
    try:
      self.mount(Markdown(content))
    except Exception:
      self.mount(Static(content))

  def show_message(self, message: str) -> None:
    self.remove_children()
    self.mount(Static(message))
