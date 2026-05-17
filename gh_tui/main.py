from __future__ import annotations

import sys

from gh_tui.app import GhTuiApp
from gh_tui.config import AppConfig


def main() -> None:
  args = sys.argv[1:]
  initial_repo = args[0] if args else None
  config = AppConfig.load()
  if initial_repo:
    config.default_repo = initial_repo
  app = GhTuiApp(config=config, initial_repo=initial_repo)
  app.run()


if __name__ == "__main__":
  main()
