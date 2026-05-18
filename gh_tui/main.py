from __future__ import annotations

import sys

from gh_tui.app import GhTuiApp
from gh_tui.config import AppConfig
from gh_tui.utils.repo_name import parse_repo_arg


def main() -> None:
  args = sys.argv[1:]
  initial_user = None
  # Support --user <username> flag (without adding new dependencies)
  if "--user" in args:
    user_index = args.index("--user")
    if user_index + 1 < len(args):
      initial_user = args[user_index + 1]
      # Remove the flag and its value so parse_repo_arg sees only repo args
      del args[user_index:user_index + 2]
    else:
      # If flag present without a value, drop the flag only
      del args[user_index]
  initial_repo = parse_repo_arg(args)
  config = AppConfig.load()
  if initial_repo:
    config.default_repo = initial_repo
  app = GhTuiApp(config=config, initial_repo=initial_repo, initial_user=initial_user)
  app.run()


if __name__ == "__main__":
  main()
