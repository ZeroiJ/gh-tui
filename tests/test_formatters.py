from gh_tui.utils.formatters import format_count


def test_format_count():
  assert format_count(500) == "500"
  assert format_count(1500) == "1.5k"
  assert format_count(1_200_000) == "1.2M"
