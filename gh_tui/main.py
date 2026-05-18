from __future__ import annotations

import sys

from gh_tui.app import GhTuiApp
from gh_tui.config import AppConfig
from gh_tui.utils.repo_name import parse_repo_arg


def main() -> None:
  args = sys.argv[1:]
  initial_repo = parse_repo_arg(args)
  config = AppConfig.load()
  if initial_repo:
    config.default_repo = initial_repo
  app = GhTuiApp(config=config, initial_repo=initial_repo)
  app.run()


if __name__ == "__main__":
  main()
