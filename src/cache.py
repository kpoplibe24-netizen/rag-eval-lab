import re
import time
from collections import OrderedDict


def normalize(question: str) -> str:
    """Normalize equivalent questions into the same cache key."""
    q = re.sub(r"\s+", " ", question.lower().strip())
    return q.rstrip("?!. ")


class TTLCache:

    def __init__(self, ttl_seconds: float, max_items: int):
        self.ttl = ttl_seconds
        self.max_items = max_items
        self._data = OrderedDict()

    def get(self, key):

        item = self._data.get(key)

        if item is None:
            return None

        expires_at, value = item

        if time.monotonic() > expires_at:
            del self._data[key]
            return None

        self._data.move_to_end(key)

        return value

    def set(self, key, value):

        self._data[key] = (
            time.monotonic() + self.ttl,
            value
        )

        self._data.move_to_end(key)

        while len(self._data) > self.max_items:
            self._data.popitem(last=False)

    def clear(self):
        self._data.clear()

    def __len__(self):
        return len(self._data)