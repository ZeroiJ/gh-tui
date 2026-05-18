# gh-tui TUI Design Document
## ASCII-Clean Aesthetic

---

## 1. Design Philosophy

**No neon borders. No thick colored lines. Just ASCII structure.**

The terminal is already a grid of characters. Instead of fighting it with heavy chrome, this design embraces:

- Thin Unicode box-drawing characters (`─│┌┐└┘├┤┬┴┼`)
- A single warm accent color (amber `#d4a373`) used sparingly
- Near-monochrome palette with subtle grays
- Content-first: the repo content is the star, UI chrome fades into the background
- Keyboard focus indicated by subtle underline or background shift, not glowing borders

---

## 2. Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `bg-primary` | `#141414` | Main content background |
| `bg-sidebar` | `#161616` | Sidebar panels (file tree, info) |
| `bg-header` | `#1a1a1a` | Header, status bar, banner backgrounds |
| `border-subtle` | `#2a2a2a` | Dividers, inactive borders, rules |
| `border-medium` | `#3a3a3a` | Input borders, modal frames |
| `text-primary` | `#e0e0e0` | Headings, selected items, important text |
| `text-secondary` | `#a0a0a0` | Body text, labels |
| `text-muted` | `#707070` | Hints, metadata, status bar text |
| `text-dim` | `#505050` | Disabled, guides, tree lines |
| `accent` | `#d4a373` | Warm amber — focus indicators, links, stars count, active states |

**Principle:** Accent color appears in <5% of the UI surface area.

---

## 3. Screen Mockups

### 3.1 Main Repo Browser (Primary Screen)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  gh-tui  ·  / search  ·  q quit                                              │  ← header
├──────────────────────────────────────────────────────────────────────────────┤
│  facebook/react                                                                │  ← banner (repo name)
├──────┬─────────────────────────────────────────────────────────┬─────────────┤
│      │                                                         │             │
│  ─ / │  # Rich                                                │ facebook/   │
│  │   │                                                         │ react       │
│  │ ▶ src                                                      │             │
│  │   │  Rich is a Python library for rich text and             │ ┌─────────┐ │
│  │ ▶ tests    beautiful formatting in the terminal.            │ │ * 45.2k │ │
│  │   │                                                         │ │ ⎕ 3.1k  │ │
│  │   │  ```python                                              │ │ ◙ 1.8k  │ │
│  │   │  from rich import print                                 │ │ # 312   │ │
│  │   │  print("[bold red]Hello[/bold red] World!")             │ └─────────┘ │
│  │   │  ```                                                   │             │
│  │   │                                                         │ lang: Python│
│  │   │  ## Features                                            │ lic: MIT    │
│  │   │                                                         │             │
│  │   │  - [x] Colors and styles                              │ upd 2d ago  │
│  │   │  - [x] Tables                                          │             │
│  │   │  - [x] Progress bars                                   │             │
│  │   │  - [x] Markdown                                        │             │
│  │   │                                                         │             │
│  │   │  ## Installation                                       │             │
│  │   │  ```bash                                               │             │
│  │   │  pip install rich                                      │             │
│  │   │  ```                                                   │             │
│  │   │                                                         │             │
│      │                                                         │             │
├──────┴─────────────────────────────────────────────────────────┴─────────────┤
│  facebook/react  │  ⚡4998/5000                                        │  ← status bar
└──────────────────────────────────────────────────────────────────────────────┘
```

**Layout proportions:**
- File tree: 28 cols (fixed), bg `#161616`, right border `#2a2a2a`
- Main content: 1fr (flex), bg `#141414`, no border
- Info panel: 28 cols (fixed), bg `#161616`, left border `#2a2a2a`

**Focus states:**
- File tree focused → right border turns `#d4a373`, bg shifts to `#181818`
- Main panel focused → bg shifts to `#181818`
- Info panel focused → left border turns `#d4a373`, bg shifts to `#181818`

---

### 3.2 File Tree Detail

When a directory is expanded, tree guides are dim gray. Selected item gets bold text + subtle background.

```
│
│ ─ /                       ← root label
│ │                         ← guide line (dim)
│ ├─▸ src                   ← directory with ▸ indicator
│ │ │ ─ components          ← expanded child
│ │ │ │   button.py         ← file, no indicator
│ │ │ │   modal.rs
│ │ │ │   tree.py
│ │ │
│ ├─▸ tests                 ← collapsed directory
│ │   ⋮                     ← placeholder
│ │
│   README.md               ← file at root level
│   LICENSE
│
```

**Tree styling:**
- Guides: `#3a3a3a` (very dim)
- Guide selected: `#d4a373` (amber accent only on active branch)
- Directory labels: bold `#e0e0e0`
- File labels: `#a0a0a0` regular weight
- Cursor row: bg `#2a2a2a`

---

### 3.3 Info Panel

ASCII box around stats instead of scattered lines.

```
┌────────────────────┐
│ facebook/react     │  ← repo name, bold
│                    │
│ Rich is a Python   │  ← description, wrapped
│ library for rich   │
│ text...            │
│                    │
│ ┌──────────────┐   │  ← stats box
│ │ *      45.2k │   │     * = star symbol
│ │ ⎕       3.1k │   │     ⎕ = fork symbol
│ │ ◙       1.8k │   │     ◙ = eye/watch symbol
│ │ #         312 │   │     # = issue symbol
│ └──────────────┘   │
│                    │
│ lang: Python       │  ← metadata
│ lic: MIT           │
│                    │
│ upd 2d ago         │  ← relative date
└────────────────────┘
```

**When no repo loaded:**
```
── gh-tui ──
│
│ search  /
│ browser b
│ refresh r
│ quit    q
└────────
```

---

### 3.4 Code View

Syntax highlighted via Pygments (monokai theme), framed by clean space.

```
┌────────────────────────────────────────────────────────┐
│ src/textual/widgets/tree.py                            │  ← filepath, bold
│                                                        │
│  1 │ from __future__ import annotations                │
│  2 │                                                    │
│  3 │ from typing import Callable, Generic, TypeVar     │
│  4 │                                                    │
│  5 │ from textual.reactive import reactive              │
│  6 │ from textual.widget import Widget                  │
│  7 │ from textual.widgets._tree import TreeNode         │
│  8 │                                                    │
│  9 │ class Tree(Widget, Generic[TreeDataType]):          │
│ 10 │     """A tree widget."""                           │
│ 11 │                                                    │
│ 12 │     DEFAULT_CSS = """                              │
│ ...│                                                    │
└────────────────────────────────────────────────────────┘
```

---

### 3.5 Search Modal

Centered dialog, thin border, no heavy chrome.

```
                              ┌─────────────────────────────────────┐
                              │ Search repositories                 │
                              │                                     │
                              │ ┌─────────────────────────────────┐ │
                              │ │ > textualize/rich               │ │  ← input
                              │ └─────────────────────────────────┘ │
                              │                                     │
                              │ ┌─────────────────────────────────┐ │
                              │ │ textualize/rich       ★ 45.2k  │ │
                              │ │ Rich is a Python library...     │ │
                              │ │                                 │ │
                              │ │ Textualize/textual    ★ 23.1k  │ │
                              │ │ Textual is a TUI framework...   │ │
                              │ │                                 │ │
                              │ │ zeroij/gh-tui          ★ 142    │ │
                              │ └─────────────────────────────────┘ │
                              │ 3 results                           │
                              └─────────────────────────────────────┘
```

**Modal styling:**
- Border: `#3a3a3a` (subtle)
- Background: `#1a1a1a`
- Input border: `#3a3a3a`, bg `#141414`
- Results: no inner border, top separator `#2a2a2a`
- No `thick $accent` border — too loud for this aesthetic

---

### 3.6 Auth Modal

```
                    ┌──────────────────────────────────────────┐
                    │ GitHub authentication                      │
                    │                                          │
                    │ Enter a classic Personal Access Token    │
                    │ for private repos and higher rate limits.  │
                    │                                          │
                    │ Create one at: github.com → Settings →   │
                    │ Developer settings → Personal access      │
                    │ tokens                                     │
                    │                                          │
                    │ ┌──────────────────────────────────────┐   │
                    │ │ ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   │   │
                    │ └──────────────────────────────────────┘   │
                    │                              [Save] [Skip] │
                    └──────────────────────────────────────────┘
```

---

### 3.7 Welcome Screen (No Repo Loaded)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  gh-tui  ·  / search  ·  q quit                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                                                                              │
│         ██████╗ ██╗  ██╗     ████████╗██╗   ██╗██╗                         │
│        ██╔════╝ ██║  ██║     ╚══██╔══╝██║   ██║██║                         │
│        ██║  ███╗███████║        ██║   ██║   ██║██║                         │
│        ██║   ██║██╔══██║        ██║   ██║   ██║██║                         │
│        ╚██████╔╝██║  ██║        ██║   ╚██████╔╝██║                         │
│         ╚═════╝ ╚═╝  ╚═╝        ╚═╝    ╚═════╝ ╚═╝                         │
│                                                                              │
│                                                                              │
│                    Welcome to gh-tui                                         │
│                                                                              │
│                    Press / then type e.g. textualize/rich                    │
│                    or run: gh-tui textualize/rich                            │
│                                                                              │
│                                                                              │
│                                                                              │
├──────────────────┬───────────────────────────────────────────┬─────────────┤
│  ─ Files          │                                           │ ─ Info      │
│  │                │                                           │ │           │
│  │   (empty)      │                                           │ │ (empty)   │
│  │                │                                           │ │           │
│  │                │                                           │ │           │
│  │                │                                           │ │           │
└──────────────────┴───────────────────────────────────────────┴─────────────┘
│  Press / to search                                                           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Component Reference

### 4.1 Borders & Dividers

| Context | Style |
|---------|-------|
| Panel separators | `solid #2a2a2a` (1px, very dark gray) |
| Focused panel edge | `solid #d4a373` (amber, only the edge toward center content) |
| Modal dialog | `solid #3a3a3a` (slightly lighter, still subtle) |
| Input fields | `solid #3a3a3a` |
| Internal rules (markdown hr) | `#2a2a2a` |

**Never use:** `thick`, `double`, `round`, or `tall` borders. Never use `$primary`, `$accent`, `$success`, `$warning`, `$error` as border colors directly.

### 4.2 Typography Hierarchy

| Level | Color | Weight | Example |
|-------|-------|--------|---------|
| H1 | `#e0e0e0` | bold | README title |
| H2 | `#c0c0c0` | bold | Section headers |
| H3+ | `#a0a0a0` | bold | Sub-sections |
| Body | `#a0a0a0` | normal | Paragraphs |
| Code | `#c0c0c0` | normal | Inline code |
| Code block bg | `#1a1a1a` | — | Fenced code bg |
| Dim/hint | `#707070` | normal | Status bar, hints |
| Muted | `#505050` | normal | Tree guides, scroll indicators |
| Accent | `#d4a373` | normal/bold | Links, focus, stars, active |

### 4.3 Scrollbars

```
background: #1a1a1a
color:      #3a3a3a
active:     #d4a373
size:       1 cell
```

Minimal 1-cell-wide scrollbar. No track, just a thumb.

### 4.4 Status Bar

```
background: #1a1a1a
color:      #707070
border-top: solid #2a2a2a

Format:  message │ location │ ⚡rate_limit
Example: Loading… │ facebook/react │ ⚡4998/5000
```

- Separator: ` │ ` (space-padded pipe)
- Rate limit amber when <100 remaining
- Stale indicator: `⊖ cache` (dim)

---

## 5. Keyboard Navigation

| Key | Action | Visual Feedback |
|-----|--------|----------------|
| `↑↓` or `k/j` | Navigate lists / scroll | Cursor row bg `#2a2a2a` |
| `→/l` or `Enter` | Expand dir / Open file | Tree expands inline |
| `←/h` or `Esc` | Collapse / Back to README | Content panel switches |
| `Tab` | Cycle focus | Target panel edge turns amber |
| `/` | Search modal | Modal fades in centered |
| `b` | Open browser | No UI change (external) |
| `r` | Refresh | Banner text: "Refreshing…" |
| `q` or `Ctrl+c` | Quit | App exits |

---

## 6. Error States

### 6.1 404 Not Found

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  gh-tui  ·  / search  ·  q quit                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    ┌─────────────────────────┐                               │
│                    │    Repository not found │                               │
│                    │                         │                               │
│                    │  ┌─────────────────┐    │                               │
│                    │  │ owner/repo-name │    │  ← input still visible        │
│                    │  └─────────────────┘    │                               │
│                    │                         │                               │
│                    │  Try another name or    │                               │
│                    │  press / to search      │                               │
│                    └─────────────────────────┘                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

Error text: `#d4a373` (amber, not red — red is too aggressive for this palette)

### 6.2 Rate Limited (403)

Banner text: `Rate limited — check your token or wait`
Status bar: `⚡0/5000` in amber

### 6.3 Network Error

Banner text: `Network error — check your connection`
Content area: `⊖ offline` with cached data if available

---

## 7. Responsive Behavior

| Terminal Width | Layout |
|----------------|--------|
| ≥120 cols | Three-column: tree (28) + content (1fr) + info (28) |
| 80-119 cols | Two-column: tree (28) + content (1fr), info panel hidden or stacked below |
| <80 cols | Single column: content only, tree as overlay toggle with `t` |

**Note:** For Phase 1 MVP, minimum width is 80 cols. Smaller terminals show a `[-] terminal too narrow` warning.

---

## 8. Animation & Motion

**Principle:** No animations. Terminal apps should feel instant.

- Data loading: banner text updates immediately, no spinner
- Panel focus: instant border color change
- Modal open/close: instant
- Search results: debounced 400ms for API, but UI updates instantly on keystroke

---

## 9. Markdown Rendering Notes

| Element | Treatment |
|---------|-----------|
| H1 | Bold `#e0e0e0`, bottom border `solid #2a2a2a` |
| H2 | Bold `#c0c0c0` |
| H3-H6 | Bold `#a0a0a0` |
| Blockquote | Left border `outer #d4a373`, text `#909090` |
| Code block | Bg `#1a1a1a`, border `solid #2a2a2a` |
| Inline code | Bg `#1a1a1a` |
| Link | `#d4a373`, underline |
| Table | Border `solid #2a2a2a`, header bg `#1a1a1a` bold |
| Horizontal rule | `#2a2a2a` |
| Bold | `#e0e0e0` bold |
| Italic | `#b0b0b0` italic |
| Strikethrough | `#505050` |

---

## 10. File Locations

| File | Purpose |
|------|---------|
| `gh_tui/styles/app.tcss` | All component styling |
| `gh_tui/widgets/file_tree.py` | Tree widget with ASCII guides |
| `gh_tui/widgets/info_panel.py` | Right panel with ASCII stat box |
| `gh_tui/widgets/status_bar.py` | Bottom bar with `│` separators |
| `gh_tui/widgets/code_view.py` | File viewer (pygments monokai) |
| `gh_tui/widgets/markdown_view.py` | README renderer |
| `DESIGN.md` | This document |

---

*Design Version: 1.0*
*Aesthetic: ASCII-Clean / Monochrome + Amber*
*Target: Textual 0.80+ / Python 3.10+*
