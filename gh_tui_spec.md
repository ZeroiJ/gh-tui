# Terminal GitHub Client — Technical Specification Document
## (For Vibe-Coding Agent)

---

## 1. PROJECT OVERVIEW

**Project Name:** `gh-tui` (working title)
**Goal:** Build an interactive Terminal User Interface (TUI) for browsing GitHub — repos, user profiles, issues, and PRs — without leaving the terminal.

**Core Philosophy:** "GitHub, reimagined for the terminal." Not a web scraper, not a thin wrapper around `git` commands. A native terminal application that fetches data from GitHub's API and renders it as a rich, keyboard-navigable interface.

---

## 2. WHAT WE ARE BUILDING

### 2.1 Target Experience
The user opens their terminal, types `gh-tui`, and lands in an interactive app. They can:
- **Browse repositories** — view README (rendered in terminal markdown), file tree, stars/forks/language stats
- **Browse user/org profiles** — avatar (ASCII/Unicode block), bio, pinned repos, contribution graph (simplified)
- **Browse Issues** — list, filter by label/state, read comments thread
- **Browse Pull Requests** — list, view diff stats, read comments, review status
- **Search** — fuzzy-find repos, users, issues across GitHub
- **Navigate** — arrow keys, `hjkl`, Tab/Shift-Tab, Enter to drill down, `q` or `Esc` to go back, `/` to search

### 2.2 Visual Style
- Rich TUI with panels, scrollable areas, syntax-highlighted code blocks, colored labels
- Responsive layout that adapts to terminal width
- Dark mode first (respect terminal color scheme)
- Minimal chrome — content-first design

---

## 3. TECH STACK RECOMMENDATION

**Primary Language: Python** (with Rust fallback for heavy lifting)

| Component | Tool | Rationale |
|-----------|------|-----------|
| TUI Framework | `Textual` (Python) | Fastest path to a "nice app" with tabs, CSS-like styling, reactive UI. Excellent docs. |
| GitHub API | `PyGithub` or `httpx` + manual REST/GraphQL | `PyGithub` for quick wins; raw GraphQL for complex nested queries (issues with comments). |
| Auth | GitHub Personal Access Token (classic or fine-grained) | Stored in `~/.config/gh-tui/token` with 0600 permissions. |
| Markdown Rendering | `rich` (built into Textual) + `markdown-it-py` | Native markdown → terminal rendering with code blocks. |
| Syntax Highlighting | `pygments` | Already integrated with Rich/Textual. |
| Caching | `shelve` or `sqlite3` (local) | Cache API responses to reduce rate-limit hits and enable offline browsing. TTL: 5 minutes for volatile data, 1 hour for static. |
| Config | `pydantic` + `toml` | User preferences, default views, keybindings. |
| Logging | `structlog` | Structured logs to `~/.local/share/gh-tui/logs/`. |

**Why Python over Rust for the agent build:**
- Textual is the most productive TUI framework available today. What takes 100 lines in Textual takes 300+ in Rust's `ratatui`.
- The bottleneck is API latency, not rendering performance. Python is "fast enough" for a network-bound TUI.
- The user knows both languages, so Python for velocity, Rust later if we need a native extension for heavy parsing.

---

## 4. ARCHITECTURE

### 4.1 High-Level Diagram

```
┌─────────────────────────────────────────┐
│           Terminal (User)               │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│           TUI Layer (Textual)            │
│  ┌─────────┐ ┌─────────┐ ┌───────────┐  │
│  │ Screens │ │ Widgets │ │ CSS Styles│  │
│  │- Repo   │ │- Sidebar│ │- Layouts  │  │
│  │- Profile│ │- Panel  │ │- Colors   │  │
│  │- Issue  │ │- Markdown│ │- Focus   │  │
│  │- PR     │ │- Code   │ │           │  │
│  └─────────┘ └─────────┘ └───────────┘  │
└─────────────┬─────────────────────────────┘
              │
┌─────────────▼─────────────────────────────┐
│         Application Layer (Python)        │
│  ┌─────────────┐  ┌──────────────────┐    │
│  │  Router     │  │  State Manager   │    │
│  │  (Screen    │  │  (Current repo,  │    │
│  │   navigation)│  │   user, filters) │    │
│  └─────────────┘  └──────────────────┘    │
│  ┌─────────────┐  ┌──────────────────┐    │
│  │  Search     │  │  Cache Manager   │    │
│  │  (Fuzzy)    │  │  (SQLite)        │    │
│  └─────────────┘  └──────────────────┘    │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│          API Layer (HTTP Client)            │
│  ┌─────────────┐      ┌──────────────┐     │
│  │ GitHub REST │      │ GitHub       │     │
│  │ (Repos,     │      │ GraphQL      │     │
│  │  Users)     │      │ (Issues, PRs │     │
│  └─────────────┘      │  with nested │     │
│                       │  comments)   │     │
│                       └──────────────┘     │
└─────────────────────────────────────────────┘
```

### 4.2 Module Structure

```
gh-tui/
├── gh_tui/
│   ├── __init__.py
│   ├── main.py              # Entry point, app bootstrap
│   ├── app.py               # Textual App class, global keybindings
│   ├── config.py            # Pydantic settings, token management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py        # Authenticated HTTP session, rate-limit handling
│   │   ├── rest.py          # REST endpoints (repos, users, search)
│   │   ├── graphql.py       # GraphQL queries (issues, PRs, comments)
│   │   └── models.py        # Dataclasses for API responses
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── base.py          # Base screen with common layout (header, footer, sidebar)
│   │   ├── repo.py          # Repository detail screen
│   │   ├── profile.py       # User/Org profile screen
│   │   ├── issue_list.py    # Issues list screen
│   │   ├── issue_detail.py  # Single issue with comments
│   │   ├── pr_list.py       # PR list screen
│   │   ├── pr_detail.py     # Single PR with diff/discussion
│   │   └── search.py        # Global search overlay
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── sidebar.py       # Navigation tree (Repo → Files, Issues, PRs)
│   │   ├── markdown_view.py # Rich markdown renderer wrapper
│   │   ├── code_view.py     # Syntax-highlighted file viewer
│   │   ├── issue_card.py    # Compact issue/PR summary widget
│   │   ├── comment_thread.py# Stack of comment widgets
│   │   ├── user_header.py   # Profile mini-card (avatar placeholder + name)
│   │   └── status_bar.py    # Bottom bar (current path, rate limit, mode)
│   ├── cache/
│   │   ├── __init__.py
│   │   └── store.py         # SQLite-backed cache with TTL
│   └── utils/
│       ├── __init__.py
│       ├── formatters.py    # Number formatting (1.2k stars), date formatting
│       └── keybindings.py   # Centralized keymap
├── styles/
│   └── app.tcss             # Textual CSS for layout
├── tests/
├── pyproject.toml
└── README.md
```

### 4.3 Data Flow Example (Viewing a Repo)

1. User types `gh-tui facebook/react` or searches and selects.
2. `Router` pushes `RepoScreen` with `repo="facebook/react"`.
3. `RepoScreen` mounts → `on_mount()` triggers async data fetch.
4. `API Client` checks Cache → miss → calls GitHub REST API (`/repos/facebook/react`).
5. Response cached → parsed into `Repository` dataclass.
6. `RepoScreen` renders:
   - Left `Sidebar`: File tree (fetched via Git Trees API), Issues tab, PRs tab
   - Center `MarkdownView`: README.md content (fetched via Contents API, rendered as markdown)
   - Right `InfoPanel`: Stars, forks, language bar, license, last updated
7. User presses `↓` → file tree focus moves → `Enter` on `src/` → fetches tree → updates sidebar.
8. User presses `Enter` on `README.md` → already loaded, scrolls to top.
9. User presses `Tab` → focus shifts to center panel → scrolls with `j/k`.

### 4.4 Key Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| REST vs GraphQL | Hybrid | REST for simple entities (repo metadata, user profiles). GraphQL for deeply nested data (issue comments, PR review threads) to minimize API calls. |
| Auth | PAT in file | Simplest for a TUI. No OAuth flow complexity. Warn user if token missing. |
| Rate Limiting | Header inspection + backoff | GitHub gives 5000 req/hour for authenticated users. Display remaining in status bar. Auto-backoff when near limit. |
| Markdown in Terminal | Rich Markdown | Handles 90% of READMEs. Fallback to raw text for edge cases. |
| Images (avatars, screenshots) | Skip or placeholder Unicode | Terminal can't display images reliably across SSH, tmux, etc. Use colored Unicode blocks or skip. |
| File Content | Raw text + syntax highlight | For code files. For binaries, show "Binary file — download via browser." |
| Offline Mode | Cache + stale-while-revalidate | If no network, show cached data with a "⚠ Offline — showing cached data" banner. |

---

## 5. THE COUNTER-ARGUMENT (Devil's Advocate)

Before the agent starts coding, here is why this project is harder than it looks, and where it might fail:

### 5.1 "GitHub's API is incomplete for 'page reimagining'"
**The Problem:** GitHub's web UI shows a *lot* of contextual data that isn't in the public API. Example: the "Used by" section, dependency graphs, security advisories, Actions status badges on repo pages, and rich PR review threads (with suggested changes, image comments).
**The Risk:** The TUI will feel like a "lite" version of GitHub. Users might open the browser anyway for complex PR reviews.
**Counter:** Scope strictly to API-available data. Call it a "GitHub Reader" not a "GitHub Replacement." For PRs, show discussion + diff stats, but defer to browser for actual line-by-line suggested-change reviews.

### 5.2 "Markdown rendering in terminal is a rabbit hole"
**The Problem:** GitHub READMEs use HTML tags, Mermaid diagrams, embedded videos, badges, and complex tables. Rich/Textual markdown handles standard CommonMark well, but chokes on raw HTML, wide tables (terminal width ~80-200 cols), and Mermaid diagrams.
**The Risk:** The "nice app" feel breaks when a README renders as garbled HTML tags or a crushed table.
**Counter:** Accept graceful degradation. Strip unsupported HTML tags. Truncate wide tables. Add a `[Open in Browser]` keybinding (`b`) for any page that renders poorly.

### 5.3 "GraphQL complexity for Issues/PRs"
**The Problem:** Issues and PRs with full comment threads require complex GraphQL queries with pagination (comments have reactions, edits, attachments). A single popular issue (e.g., 500 comments) could be 50+ API calls.
**The Risk:** Slow loading, rate limit exhaustion, janky UI while paginating.
**Counter:** Implement aggressive pagination — load first 20 comments, "Load more" button. Cache comment threads permanently (they rarely change). Use REST for issue lists (faster), GraphQL only for detail views.

### 5.4 "Private repos + Enterprise GitHub = auth hell"
**The Problem:** Fine-grained PATs have scope limitations. Enterprise GitHub (GHES) uses different API URLs. SSO-enabled orgs require token authorization.
**The Risk:** "It works on my public repos but not my work repos" — the most common user complaint.
**Counter:** Start with classic PATs (broader scope). Add GHES URL config later. Document auth setup clearly in README.

### 5.5 "TUI frameworks have a 'uncanny valley'"
**The Problem:** Textual is great, but terminal apps never feel as smooth as GUI apps. Resizing, mouse support, and color scheme detection vary across terminals (iTerm vs Windows Terminal vs Linux tty).
**The Risk:** The app looks amazing in iTerm2 on macOS, but broken in Windows Terminal or over SSH.
**Counter:** Test early on target terminals. Avoid mouse-dependent interactions — make everything keyboard-accessible. Stick to standard 256 colors + bold/italic.

### 5.6 "This is a lot of screens for a 'vibe code' session"
**The Problem:** 6+ screens, API client, cache layer, config, error handling, pagination, search — this is 3000+ lines of code, not a 200-line script.
**The Risk:** The agent generates a beautiful skeleton that crashes on real data, or a working demo that only handles public repos and crashes on anything else.
**Counter:** Phase the build ruthlessly. Phase 1 must be *complete and shippable* on its own. Do not build half of 6 screens. Build 100% of 1 screen.

---

## 6. FINAL REFINED SPEC (What The Agent Should Actually Build)

After weighing the counter-arguments, here is the scoped, realistic build plan:

### 6.1 Revised Philosophy
**"A beautiful, keyboard-driven GitHub repo browser."** 
- Not a full GitHub replacement.
- Not a git client (no clone/commit/push).
- A **reader/browser** for GitHub content in the terminal.

### 6.2 MVP Scope (Phase 1 — The Only Phase for Vibe-Coding Round 1)

**Goal:** A single, polished screen that makes the user say "wow, I can actually use this."

**Included:**
1. **Repo Browser Screen** (the only screen for now)
   - Search bar at top (`/` to activate) — search GitHub repos via API
   - Select a repo → full repo view
   - Left sidebar: file tree (collapsible folders)
   - Center: README rendered as rich markdown (scrollable)
   - Right panel: repo stats (stars, forks, language, license, description)
   - Bottom status bar: current repo, GitHub API rate limit remaining

2. **File Viewer** (within Repo Browser)
   - Click/enter a file in sidebar → center panel switches to code view with syntax highlighting
   - Click/enter a folder → sidebar expands
   - `b` key → opens current file/repo in default browser
   - `Esc` or `h` → back to README view

3. **Authentication**
   - On first run, prompt for GitHub PAT (classic)
   - Store in `~/.config/gh-tui/config.toml`
   - If no token, work in public-only mode with lower rate limits

4. **Caching**
   - SQLite cache for repo metadata, README content, file trees
   - TTL: 10 minutes
   - Show "⚠ Stale" indicator if data is cached but older than TTL

**Explicitly Deferred (Phase 2+):**
- User profiles (Phase 2)
- Issues list and detail (Phase 3)
- PR list and detail (Phase 4)
- Offline mode without cache (Phase 2 — just show error for now)
- Enterprise GitHub support (Phase 4)
- Custom themes/keybindings (Phase 3)

### 6.3 Success Criteria for Phase 1
- [ ] Can launch `gh-tui`
- [ ] Can search for any public repo (e.g., `facebook/react`)
- [ ] Can browse file tree and view files with syntax highlighting
- [ ] Can view README with proper markdown formatting and code blocks
- [ ] Can navigate entirely with keyboard (arrows, enter, esc, /, b, q)
- [ ] Authenticated users can view their private repos
- [ ] App handles API errors gracefully (rate limit, 404, network down)
- [ ] App is installable via `pip install -e .`

### 6.4 Non-Goals (Protect Scope)
- No git operations (clone, branch, commit)
- No issue/PR creation or editing (read-only for Phase 1)
- No image rendering (avatars, screenshots)
- No real-time notifications
- No multi-account support

---

## 7. IMPLEMENTATION CHECKLIST FOR AGENT

### Step 1: Project Skeleton
- [ ] `pyproject.toml` with dependencies: `textual`, `httpx`, `pygithub`, `pydantic`, `pygments`
- [ ] `styles/app.tcss` with basic layout (sidebar 25%, main 50%, info 25%)
- [ ] `main.py` entry point

### Step 2: API Layer
- [ ] `api/client.py`: Authenticated `httpx.AsyncClient`, rate-limit header parser
- [ ] `api/rest.py`: `search_repos()`, `get_repo()`, `get_readme()`, `get_tree()`, `get_file_content()`
- [ ] `api/models.py`: `Repository`, `FileTree`, `ContentFile` dataclasses

### Step 3: Cache Layer
- [ ] `cache/store.py`: SQLite init, `get(key)`, `set(key, value, ttl)`, `clear()`

### Step 4: Core Widgets
- [ ] `widgets/sidebar.py`: `Tree` widget for file navigation
- [ ] `widgets/markdown_view.py`: `Markdown` widget wrapper
- [ ] `widgets/code_view.py`: `Static` widget with Pygments-highlighted text
- [ ] `widgets/status_bar.py`: Footer with repo name + rate limit

### Step 5: Repo Screen
- [ ] `screens/repo.py`: Compose layout, handle data loading, wire widgets
- [ ] Keyboard navigation: arrows in sidebar, Enter to open, Esc to go back, `/` for search overlay

### Step 6: Search Overlay
- [ ] `screens/search.py`: Modal overlay with `Input` → hits search API → `ListView` of results → Enter opens repo

### Step 7: Auth & Config
- [ ] `config.py`: Pydantic model, load/save TOML, prompt for token if missing

### Step 8: Polish
- [ ] Error handling: 404 → "Repo not found", 403 → "Rate limited. Check token.", network → "Network error"
- [ ] Loading states: Spinner while fetching
- [ ] `README.md` with install and auth instructions

---

## 8. KEY COMMANDS & NAVIGATION

| Key | Action |
|-----|--------|
| `↑/↓` or `k/j` | Navigate lists / scroll |
| `→/l` or `Enter` | Expand folder / Open file / Select |
| `←/h` or `Esc` | Collapse folder / Go back / Close overlay |
| `Tab` | Cycle focus between sidebar → main panel → info panel |
| `/` | Open search overlay |
| `b` | Open current page in browser |
| `r` | Refresh current data (bypass cache) |
| `q` or `Ctrl+c` | Quit |

---

## 9. RISK MITIGATION SUMMARY

| Risk | Mitigation |
|------|------------|
| API rate limits | Cache aggressively; display remaining quota; classic PAT for 5000/hr |
| Markdown edge cases | Graceful degradation; `b` key to open browser for broken renders |
| Terminal compatibility | Keyboard-first; no mouse-required interactions; 256-color safe |
| Scope creep | **Strict Phase 1 boundary.** Only repo browser + file viewer + search. |
| Auth complexity | Classic PAT only for MVP. Document setup. |

---

## 10. FINAL VERDICT

**Is this possible?** Yes. 
**Is this easy?** No — but Phase 1 is achievable in a focused vibe-coding session.
**Will it replace the browser?** No, and it shouldn't try to yet. But it will make browsing repos from the terminal genuinely pleasant.

**Agent Instruction:** Build Phase 1 exactly as specified. Do not add features. Do not build Phase 2 screens. Make the repo browser so polished that the user wants to use it daily. Then we will expand.

---

*Document Version: 1.0*
*Target: Python 3.10+, Textual 0.x*
*Date: 2026-05-17*
