from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Repository:
    full_name: str
    description: str | None
    stars: int
    forks: int
    watchers: int
    language: str | None
    license_name: str | None
    html_url: str
    default_branch: str
    updated_at: str
    open_issues: int
    is_private: bool


@dataclass(frozen=True)
class SearchResult:
    full_name: str
    description: str | None
    stars: int
    language: str | None
    html_url: str


@dataclass(frozen=True)
class TreeEntry:
    name: str
    path: str
    entry_type: str  # "file" | "dir"
    size: int | None
    sha: str | None = None


@dataclass(frozen=True)
class ContentFile:
    path: str
    name: str
    content: str
    encoding: str
    size: int
    html_url: str
    is_binary: bool = False
