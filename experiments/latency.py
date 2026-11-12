import sys
import time

sys.path.insert(0, "src")

from methods import hybrid_search, rerank_search

qs = [
    "how to read headers?",
    "how do I validate request body?",
    "what is dependency injection?"
] * 5

for name, fn in [
    ("hybrid", hybrid_search),
    ("rerank", rerank_search)
]:

    fn(qs[0], k=5, max_words=200)

    start = time.perf_counter()

    for q in qs:
        fn(q, k=5, max_words=200)

    elapsed = time.perf_counter() - start

    print(
        name,
        f"{elapsed / len(qs) * 1000:.0f} ms/query"
    )