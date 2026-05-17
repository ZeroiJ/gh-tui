from __future__ import annotations

from datetime import datetime, timezone


def format_count(n: int) -> str:
  if n >= 1_000_000:
    val = f"{n / 1_000_000:.1f}".rstrip("0").rstrip(".")
    return f"{val}M"
  if n >= 1_000:
    val = f"{n / 1_000:.1f}".rstrip("0").rstrip(".")
    return f"{val}k"
  return str(n)


def format_relative_date(iso_date: str) -> str:
  try:
    dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
  except ValueError:
    return iso_date
  now = datetime.now(timezone.utc)
  delta = now - dt
  days = delta.days
  if days == 0:
    hours = delta.seconds // 3600
    if hours == 0:
      minutes = max(1, delta.seconds // 60)
      return f"{minutes}m ago"
    return f"{hours}h ago"
  if days < 30:
    return f"{days}d ago"
  if days < 365:
    return f"{days // 30}mo ago"
  return f"{days // 365}y ago"
