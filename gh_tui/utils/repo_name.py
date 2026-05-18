from __future__ import annotations

import re

_REPO_RE = re.compile(r"^[\w.\-]+/[\w.\-]+(?:\.git)?$")


def normalize_repo_query(text: str) -> str:
  """Strip wrappers so 'gh-tui textualize/rich' becomes 'textualize/rich'."""
  text = text.strip()
  if text.startswith("gh-tui "):
    text = text[7:].strip()
  if text.startswith("https://github.com/"):
    text = text.removeprefix("https://github.com/").strip("/")
  if text.endswith(".git"):
    text = text[:-4]
  return text


def looks_like_repo_name(query: str) -> bool:
  query = normalize_repo_query(query)
  return bool(_REPO_RE.match(query))


def parse_repo_arg(args: list[str]) -> str | None:
  """Parse CLI args into owner/repo."""
  if not args:
    return None
  if len(args) == 1:
    normalized = normalize_repo_query(args[0])
    return normalized if looks_like_repo_name(normalized) else None
  # gh-tui textualize/rich  →  user passed command name as first arg by mistake
  if args[0] == "gh-tui":
    return normalize_repo_query(args[1])
  joined = normalize_repo_query(" ".join(args))
  if looks_like_repo_name(joined):
    return joined
  combined = f"{args[0]}/{args[1]}"
  return combined if looks_like_repo_name(combined) else None
