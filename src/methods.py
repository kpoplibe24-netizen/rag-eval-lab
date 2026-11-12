import re
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

from ingest import build_chunks
from retrieve import search as dense_search


def tokenize(text: str):
    return re.findall(r"[a-z0-9_]+", text.lower())


_bm25_cache = {}


def _get_bm25(max_words):
    if max_words not in _bm25_cache:
        chunks = build_chunks("data/docs", max_words)
        bm25 = BM25Okapi([tokenize(c.text) for c in chunks])
        _bm25_cache[max_words] = (bm25, chunks)

    return _bm25_cache[max_words]


def bm25_search(question, k=10, max_words=300):
    bm25, chunks = _get_bm25(max_words)

    scores = bm25.get_scores(tokenize(question))

    top = sorted(
        range(len(chunks)),
        key=lambda i: scores[i],
        reverse=True
    )[:k]

    return [
        {
            "file": chunks[i].file,
            "heading": chunks[i].heading,
            "text": chunks[i].text,
            "score": float(scores[i])
        }
        for i in top
    ]


def hybrid_search(question, k=10, max_words=300, pool=30, rrf_k=60):
    """Combine dense and sparse rankings using Reciprocal Rank Fusion."""

    dense = dense_search(question, k=pool, max_words=max_words)
    sparse = bm25_search(question, k=pool, max_words=max_words)

    fused = {}

    for ranking in (dense, sparse):
        for rank, r in enumerate(ranking, start=1):

            key = (r["file"], r["heading"], r["text"])

            if key not in fused:
                fused[key] = {**r, "score": 0.0}

            fused[key]["score"] += 1 / (rrf_k + rank)

    return sorted(
        fused.values(),
        key=lambda r: r["score"],
        reverse=True
    )[:k]


_reranker = None


def rerank_search(question, k=10, max_words=300, pool=20):
    """Retrieve candidates using hybrid search, then rerank them."""

    global _reranker

    if _reranker is None:
        _reranker = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    candidates = hybrid_search(
        question,
        k=pool,
        max_words=max_words
    )

    scores = _reranker.predict(
        [(question, c["text"]) for c in candidates]
    )

    for candidate, score in zip(candidates, scores):
        candidate["score"] = float(score)

    return sorted(
        candidates,
        key=lambda r: r["score"],
        reverse=True
    )[:k]