# Changelog

All notable changes to **gh-tui** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- User/org profile screens (Phase 2)
- Issues list and detail views (Phase 3)
- Pull request list and detail views (Phase 4)

## [0.1.0] - 2026-05-17

### Added
- Initial Phase 1 MVP: keyboard-driven GitHub repository browser
- Repo browser screen with file tree, README markdown view, and syntax-highlighted code viewer
- Right info panel (stars, forks, language, license, description, last updated)
- Bottom status bar (current repo/path, API rate limit remaining)
- Search overlay (`/`) via GitHub repository search API
- First-run authentication prompt; token stored in `~/.config/gh-tui/config.toml`
- Public-only mode without a token (lower rate limits)
- SQLite cache with 10-minute TTL (`~/.local/share/gh-tui/cache.db`)
- Stale-cache indicator when serving cached data offline or past TTL
- Keybindings: arrows/hjkl, Enter, Esc/h, Tab, `/`, `b`, `r`, `q`
- CLI entry point: `gh-tui` and `gh-tui owner/repo`
- Install via `pip install -e .`

### Notes
- Read-only; no git operations, issues, or pull requests in this release
- Classic GitHub PAT only; no Enterprise GitHub support yet

[Unreleased]: https://github.com/ZeroiJ/gh-tui/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ZeroiJ/gh-tui/releases/tag/v0.1.0
