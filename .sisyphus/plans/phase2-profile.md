# Phase 2 Plan — User/Org Profile Screen

## Goal

Add a `ProfileScreen` that shows a GitHub user or organization's profile: bio, stats (followers, following, public repos), a list of their repositories (clickable → opens repo browser), and a link to open in browser.

**Entry points:**
1. From `RepoScreen`: press `u` on the owner name in the info panel → opens profile for that repo's owner
2. From `SearchScreen`: type `user:ZeroiJ` → search API returns user results → select → opens profile
3. From CLI: `gh-tui --user ZeroiJ` → opens profile directly

---

## Architecture

### Screen Flow

```
RepoScreen (base)
    │
    ├── press "u" → ProfileScreen(owner="facebook")
    │       ├── left: repo list (ListView, clickable → opens repo)
    │       ├── right: profile info (InfoPanel with show_user())
    │       └── bottom: status bar
    │
    └── press "/" → SearchScreen → select repo → RepoScreen
```

### What Gets Reused

| Component | How |
|-----------|-----|
| `InfoPanel` | Add `show_user()` method alongside `show_repo()` — same ASCII box pattern |
| `StatusBar` | No changes needed — `update_status(repo=login, ...)` works for profiles |
| `ListView` pattern | From `SearchScreen` — flat repo list with `ListItem.data` |
| `GitHubClient` | Add `get_user()`, `get_user_repos()` methods |
| `cache/store.py` | Same TTL cache, new cache keys |
| `utils/formatters.py` | `format_count()`, `format_relative_date()` directly applicable |
| CSS palette | All colors, borders, focus states already defined |

### What Gets Created

| File | Purpose |
|------|---------|
| `api/models.py` | Add `UserProfile` dataclass |
| `api/client.py` | Add `get_user()`, `get_user_repos()` |
| `api/rest.py` | Add `parse_user()`, `parse_user_repo_list()` |
| `screens/profile.py` | New `ProfileScreen(Screen)` |
| `screens/__init__.py` | Export `ProfileScreen` |
| `screens/repo.py` | Add binding `u` + `action_open_profile()` |
| `styles/app.tcss` | Add `ProfileScreen` layout CSS |
| `main.py` | Add `--user` CLI arg |

---

## Data Model

### `UserProfile` (from `GET /users/{username}`)

```python
@dataclass(frozen=True)
class UserProfile:
    login: str
    name: str | None
    bio: str | None
    company: str | None
    location: str | None
    blog: str | None
    twitter_username: str | None
    public_repos: int
    followers: int
    following: int
    html_url: str
    avatar_url: str  # not rendered, stored for future use
    type: str  # "User" or "Organization"
    created_at: str
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /users/{username}` | `get_user(login)` | Profile metadata |
| `GET /users/{username}/repos?sort=updated&per_page=30` | `get_user_repos(login)` | User's repos list |

**Note:** Pinned repos require GraphQL — skipped for Phase 2. Show top repos by `updated` instead.

---

## ProfileScreen Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  gh-tui  ·  / search  ·  q quit                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  facebook                                                                    │  ← banner (username)
├──────────────────────────────────────────────────────────────┬───────────────┤
│                                                              │               │
│  ┌────────────────────────────────────────────────────────┐ │ facebook    │
│  │ Facebook                                               │ │             │
│  │                                                        │ │ ┌─────────┐ │
│  │ The social network.                                    │ │ │ ◙ 1.2k  │ │
│  │                                                        │ │ │ ★ 45.2k │ │
│  │ Menlo Park, CA  ·  facebook.com                        │ │ │ ⎕ 3.1k  │ │
│  │                                                        │ │ └─────────┘ │
│  │ ┌──────────────────────────────────────────────────┐   │ │             │
│  │ │ textualize/textual              ★ 23.1k Python   │   │ │ joined 3y  │
│  │ │ ZeroiJ/gh-tui                   ★ 142  Python    │   │ │ ago         │
│  │ │ ...more repos...                                 │   │ │             │
│  │ └──────────────────────────────────────────────────┘   │ │ type: Org   │
│  │                                                        │ │             │
├──────────────────────────────────────────────────────────────┴───────────────┤
│  facebook  │  ⚡4998/5000                                                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Layout proportions:**
- Repo list (left): 1fr (flexible)
- Profile info (right): 28 cols (fixed)

---

## Implementation Steps

### Step 1: API Layer (models + client + rest)
- Add `UserProfile` dataclass to `api/models.py`
- Add `get_user(login)` and `get_user_repos(login)` to `api/client.py`
- Add `parse_user(data)` and `parse_user_repo_list(data)` to `api/rest.py`

### Step 2: InfoPanel Extension
- Add `show_user(user: UserProfile, stale: bool)` method to `InfoPanel`
- ASCII box: followers, following, public repos
- Metadata: company, location, blog, joined date, type

### Step 3: ProfileScreen
- Create `screens/profile.py`
- Layout: header, banner, Horizontal(repo_list + info_panel), status_bar
- `load_user(login)` worker: fetches profile + repos
- `ListView` for repos: each item clickable → opens `RepoScreen` via callback
- Keybindings: `Esc`/`h` → go back to repo screen, `b` → open profile in browser, `/` → search, `Enter` → open selected repo

### Step 4: Navigation Wiring
- Add `u` binding to `RepoScreen` → `action_open_profile()` extracts owner from `self._repo_name`
- `ProfileScreen` dismisses with selected repo name (or None) → callback opens `RepoScreen`
- Update `screens/__init__.py` to export `ProfileScreen`

### Step 5: CSS
- Add `ProfileScreen` layout rules to `app.tcss`
- Match existing palette: `#141414`, `#161616`, `#2a2a2a`, `#d4a373`

### Step 6: CLI Support (optional)
- Add `--user` flag to `main.py` → opens `ProfileScreen` directly

---

## Keybindings (ProfileScreen)

| Key | Action |
|-----|--------|
| `↑/↓` or `j/k` | Navigate repo list |
| `Enter` | Open selected repo → pushes `RepoScreen` |
| `Esc`/`h` | Go back to previous screen |
| `Tab` | Cycle focus between repo list and info panel |
| `b` | Open profile in browser |
| `/` | Open search overlay |
| `r` | Refresh (bypass cache) |
| `q` | Quit |

---

## Success Criteria

- [ ] Can navigate from repo → owner profile (`u` key)
- [ ] Profile shows: name, bio, location, company, followers, following, public repos, joined date
- [ ] Repo list shows user's repos with star count and language
- [ ] Clicking a repo opens it in `RepoScreen`
- [ ] `Esc`/`h` returns to previous screen
- [ ] `b` opens profile URL in browser
- [ ] Works for both users and organizations
- [ ] Handles 404 (user not found) gracefully
- [ ] CSS matches DESIGN.md palette

---

## Out of Scope (Phase 3+)

- Pinned repos (requires GraphQL)
- Contribution graph / activity feed
- Followers/following lists
- Organization members list
- Avatar rendering (ASCII placeholder only)
- User search (search API returns repos, not users)
