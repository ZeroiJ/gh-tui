import tempfile
from pathlib import Path

from gh_tui.cache.store import CacheStore


def test_cache_set_and_get():
  with tempfile.TemporaryDirectory() as tmp:
    store = CacheStore(Path(tmp) / "cache.db")
    store.set("key", {"a": 1}, ttl_seconds=60)
    value, stale = store.get("key")
    assert value == {"a": 1}
    assert stale is False


def test_cache_missing():
  with tempfile.TemporaryDirectory() as tmp:
    store = CacheStore(Path(tmp) / "cache.db")
    value, stale = store.get("missing")
    assert value is None
    assert stale is False
