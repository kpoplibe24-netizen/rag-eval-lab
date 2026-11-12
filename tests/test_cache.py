import time

from cache import TTLCache, normalize


def test_normalize():
    assert normalize("  HOW   TO   USE FastAPI??? ") == "how to use fastapi"


def test_set_and_get():
    cache = TTLCache(ttl_seconds=60, max_items=10)

    cache.set("question", {"answer": "FastAPI"})

    assert cache.get("question") == {"answer": "FastAPI"}


def test_missing_key():
    cache = TTLCache(ttl_seconds=60, max_items=10)

    assert cache.get("missing") is None


def test_expired_item():
    cache = TTLCache(ttl_seconds=0.01, max_items=10)

    cache.set("question", "answer")

    time.sleep(0.02)

    assert cache.get("question") is None


def test_lru_eviction():
    cache = TTLCache(ttl_seconds=60, max_items=2)

    cache.set("A", 1)
    cache.set("B", 2)

    # Access A, making B the least recently used.
    cache.get("A")

    cache.set("C", 3)

    assert cache.get("A") == 1
    assert cache.get("B") is None
    assert cache.get("C") == 3


def test_clear():
    cache = TTLCache(ttl_seconds=60, max_items=10)

    cache.set("A", 1)
    cache.clear()

    assert len(cache) == 0
    assert cache.get("A") is None