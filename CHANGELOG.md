# Changelog

All notable changes to **gh-tui** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Handoff context (for Agentic CLI / new sessions)

### What we are building

**gh-tui** is a Terminal User Interface (TUI) that reimagines **GitHub as a native terminal app** — browse repos, file trees, READMEs, and source files with the keyboard, without opening a browser. It is **read-only** (no git clone/commit, no issues/PRs yet).

**Repo:** https://github.com/ZeroiJ/gh-tui  
**Stack:** Python 3.10+, [Textual](https://textual.textualize.io/), `httpx` (GitHub REST API), `pydantic` + TOML config, SQLite cache (10 min TTL), Pygments syntax highlighting.

### Phase 1 scope (current — build only this until Phase 1 is polished)

| In scope | Out of scope (deferred) |
|----------|-------------------------|
| Single repo browser screen | User/org profiles (Phase 2) |
| Search repos (`/`) | Issues list/detail (Phase 3) |
| File tree + README markdown + code view | PR list/detail (Phase 4) |
| Repo stats panel + status bar | Enterprise GitHub, custom themes |
| PAT auth + public-only mode | Offline mode without cache |

### What exists today (implemented)

```
gh_tui/
├── main.py              # CLI entry: gh-tui [owner/repo]
├── app.py               # Textual App; push_screen(RepoScreen); auth worker
├── config.py            # ~/.config/gh-tui/config.toml
├── api/                 # GitHubClient, rest.py, models.py
├── cache/store.py       # SQLite TTL cache
├── screens/
│   ├── repo.py          # Main screen (only screen in normal use)
│   ├── search.py        # Modal search overlay
│   └── auth.py          # First-run PAT prompt
├── widgets/             # FileTree, MarkdownView, CodeView, InfoPanel, StatusBar
├── styles/app.tcss
└── utils/repo_name.py   # Normalize owner/repo from CLI and search
```

**Keybindings:** `/` search · `↑↓`/`jk` tree · `Enter` open · `Esc`/`h` README · `Tab` panels · `b` browser · `r` refresh · `q` quit

**Run:**
```bash
cd gh-tui && pip install -e .
gh-tui                      # welcome screen; press /
gh-tui textualize/rich      # open repo directly
```

**Auth:** `~/.config/gh-tui/config.toml` or `GITHUB_TOKEN` / `GH_TOKEN`. Public-only works without token (~60 req/hr).

### What to read first (in order)

1. **`gh_tui_spec.md`** — Full product spec, architecture diagram, Phase 1 checklist, risks, keybindings. **Source of truth for scope.**
2. **`README.md`** — Install, auth, usage summary.
3. **`gh_tui/app.py`** + **`gh_tui/screens/repo.py`** — App bootstrap and main UI flow.
4. **`gh_tui/api/client.py`** + **`gh_tui/screens/search.py`** — API + search behavior.
5. **`CHANGELOG.md`** (this file) — Recent fixes and handoff notes.

### Bugs fixed in this development cycle (do not regress)

- **`NoActiveWorker`:** `push_screen_wait` must run inside `@work`, not `on_mount` directly.
- **Blank screen:** Do not `yield RepoScreen()` in `App.compose()` — use `push_screen(RepoScreen(...))` in `on_mount`.
- **`push_screen(..., name=)`:** Invalid in current Textual; keep `self._repo_screen` reference instead.
- **Layout:** No `dock: left/right` inside `Horizontal`; CSS targets `RepoScreen`; use `on_ready` for initial content.
- **Search query `gh-tui textualize/rich`:** Returns 0 GitHub results — use `textualize/rich` only; `utils/repo_name.py` strips `gh-tui ` prefix.
- **Crash on `owner/repo` in search:** Repo names must not be Textual widget `id`s (no `/`); store on `ListItem.data` after construction (not `data=` kwarg).
- **Not Hugging Face:** Errors mentioning `huggingface/transformers` are Textual ID validation, not ML dependencies.
- **Search rate limit exhaustion:** Every keystroke after 2 chars fired an API call; fixed with 400ms debounce (`asyncio.sleep` + `exclusive=True` worker).
- **`AttributeError` on debounce task:** `run_worker()` returns Textual `Worker`, not `asyncio.Task` — `.done` attribute doesn't exist; fixed by using `_search_query` instance variable + `exclusive=True` auto-cancellation.
- **CSS `scrollbar-size: 1`:** Invalid in Textual — requires two values (horizontal, vertical); fixed to `scrollbar-size: 1 1`.
- **CSS `#primary-background`:** Invalid hex color in `search.py` `DEFAULT_CSS` — treated as comment by parser; fixed to `border-top: solid #2a2a2a`.
- **Banner stuck on "Loading…":** After successful repo load, banner was never cleared; fixed by setting banner to repo name on success.
- **Loading message used `[cyan]`:** Violates DESIGN.md monochrome+amber palette; fixed to use default text color.

### Suggested next work (Phase 1 polish or Phase 2)

- [ ] Commit/push unreleased fixes if not already on `main`
- [ ] More integration tests (search → load repo mock)
- [ ] Phase 2: profile screen (see `gh_tui_spec.md` §6.2 deferred list)
- [ ] GraphQL layer for issues/PRs (Phase 3+)

### Tests

```bash
pytest tests/ -q   # cache, formatters, rest, repo_name
```

---

## [Unreleased]

### Fixed
- `NoActiveWorker` when showing auth dialog on first run (`@work` wrapper for `push_screen_wait`)
- Blank main screen: mount `RepoScreen` via `push_screen()` instead of yielding it in `App.compose()`
- `TypeError` from invalid `name=` argument on `push_screen` (use `self._repo_screen` reference)
- Layout collapse from `dock` in horizontal panels; status bar no longer uses `dock: bottom`
- Welcome/README content shown in `on_ready` after layout is calculated
- Post-auth UI refresh via `after_auth()` on repo screen
- Repo CLI/search parsing: `gh-tui textualize/rich` → `textualize/rich` (`utils/repo_name.py`)
- Search opens `owner/repo` directly when input looks like a repo name (no GitHub search API call)
- Crash when selecting repos with `/` in name (e.g. `huggingface/transformers`): use `ListItem.data`, not `id=`
- `TypeError` from `ListItem(..., data=...)`: set `row.data = {...}` after construction
- Loading and error states shown in center panel, not only banner
- Empty-token save on auth treated as skip (public-only)
- Search keystroke spam exhausting rate limit: added 400ms debounce via `asyncio.sleep` + `exclusive=True` worker
- `AttributeError` on debounce task: `run_worker()` returns Textual `Worker` (no `.done`); fixed with `_search_query` instance variable
- CSS `scrollbar-size: 1` invalid value → `scrollbar-size: 1 1`
- CSS `#primary-background` invalid hex in `search.py` → `border-top: solid #2a2a2a`
- Banner stuck on "Loading…" after successful repo load → now shows repo name
- Loading message `[cyan]` color violating DESIGN.md palette → neutral text color
- Welcome screen missing ASCII art header per DESIGN.md spec

### Changed
- Welcome text clarifies: do not type `gh-tui` in the search box
- `CHANGELOG` GitHub links point to `ZeroiJ/gh-tui`

### Planned (Phase 2+)
- User/org profile screens
- Issues list and detail views
- Pull request list and detail views

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
- MIT `LICENSE`

### Notes
- Read-only; no git operations, issues, or pull requests in this release
- Classic GitHub PAT only; no Enterprise GitHub support yet

[Unreleased]: https://github.com/ZeroiJ/gh-tui/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ZeroiJ/gh-tui/releases/tag/v0.1.0
