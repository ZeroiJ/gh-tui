from __future__ import annotations

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
from pygments.util import ClassNotFound
from rich.text import Text
from textual.containers import VerticalScroll
from textual.widgets import Static


class CodeView(VerticalScroll):
  """Syntax-highlighted file viewer."""

  DEFAULT_CSS = """
  CodeView {
    width: 1fr;
    min-width: 24;
    height: 100%;
    border: solid $primary-background;
    padding: 1 2;
  }
  """

  def show_file(
    self,
    path: str,
    content: str,
    *,
    language: str | None = None,
    is_binary: bool = False,
  ) -> None:
    self.remove_children()
    self.mount(Static(f"[bold]{path}[/bold]\n"))

    if is_binary:
      self.mount(
        Static("[dim]Binary file — open in browser with [bold]b[/bold][/dim]")
      )
      return

    if len(content) > 500_000:
      content = content[:500_000] + "\n\n… [truncated — file too large]"
    self.mount(Static(self._highlight(path, content, language)))

  def show_message(self, message: str) -> None:
    self.remove_children()
    self.mount(Static(message))

  def _highlight(
    self, path: str, content: str, language: str | None
  ) -> Text:
    lexer = None
    if language:
      try:
        lexer = get_lexer_by_name(language)
      except ClassNotFound:
        pass
    if lexer is None:
      try:
        lexer = guess_lexer_for_filename(path, content)
      except ClassNotFound:
        from pygments.lexers import TextLexer

        lexer = TextLexer()
    try:
      result = highlight(
        content,
        lexer,
        Terminal256Formatter(style="monokai"),
      )
      return Text.from_ansi(result)
    except Exception:
      return Text(content)
