from gh_tui.utils.repo_name import (
  looks_like_repo_name,
  normalize_repo_query,
  parse_repo_arg,
)


def test_normalize_repo_query():
  assert normalize_repo_query("gh-tui textualize/rich") == "textualize/rich"
  assert (
    normalize_repo_query("https://github.com/Textualize/rich")
    == "Textualize/rich"
  )


def test_parse_repo_arg():
  assert parse_repo_arg(["textualize/rich"]) == "textualize/rich"
  assert parse_repo_arg(["gh-tui", "textualize/rich"]) == "textualize/rich"
  assert parse_repo_arg(["gh-tui textualize/rich"]) == "textualize/rich"
  assert parse_repo_arg(["textualize", "rich"]) == "textualize/rich"


def test_looks_like_repo_name():
  assert looks_like_repo_name("textualize/rich")
  assert not looks_like_repo_name("python tui")
