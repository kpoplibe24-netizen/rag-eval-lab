import asyncio
import logging
import time

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import config
import db

from cache import TTLCache, normalize
from methods import rerank_search
from llm import generate_answer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REFUSAL_TEXT = (
    "I couldn't find an answer to that in the FastAPI documentation "
    "I have indexed."
)

cache = TTLCache(
    ttl_seconds=config.CACHE_TTL_SECONDS,
    max_items=config.CACHE_MAX_ITEMS
)


async def retrieve(question):
    """Run retrieval in a separate thread."""

    return await asyncio.to_thread(
        rerank_search,
        question,
        k=config.TOP_K,
        max_words=config.MAX_WORDS
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()

    app.state.threshold = config.load_threshold()

    # Load retrieval models and prepare the index before serving requests.
    await retrieve("warm up")

    logger.info("RAG service is ready.")

    yield


app = FastAPI(
    title="RAG Evaluation Service",
    description="A RAG service with hybrid retrieval, reranking and refusal handling.",
    version="1.0.0",
    lifespan=lifespan
)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class Source(BaseModel):
    file: str
    heading: str
    score: float


class AskResponse(BaseModel):
    answer: str
    refused: bool
    cached: bool
    top_score: float | None
    sources: list[Source]
    latency_ms: float


async def log_query(row):
    """Log a request without allowing database errors to break the API."""

    try:
        await asyncio.to_thread(db.log_query, row)
    except Exception:
        logger.exception("Failed to log query.")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "cache_items": len(cache)
    }


@app.get("/stats")
async def stats():
    return await asyncio.to_thread(db.get_stats)


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):

    start_time = time.perf_counter()

    question = request.question
    cache_key = normalize(question)

    # 1. Check cache
    cached_result = cache.get(cache_key)

    if cached_result is not None:

        latency_ms = (time.perf_counter() - start_time) * 1000

        await log_query({
            "ts": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "cache_hit": True,
            "refused": cached_result["refused"],
            "top_score": cached_result["top_score"],
            "latency_ms": latency_ms,
            "retrieval_ms": 0,
            "llm_ms": 0
        })

        return AskResponse(
            **cached_result,
            cached=True,
            latency_ms=latency_ms
        )

    # 2. Retrieve and rerank documents
    retrieval_start = time.perf_counter()

    chunks = await retrieve(question)

    retrieval_ms = (
        time.perf_counter() - retrieval_start
    ) * 1000

    top_score = float(chunks[0]["score"]) if chunks else None

    llm_ms = 0.0

    # 3. Apply refusal threshold
    if not chunks or top_score < app.state.threshold:

        result = {
            "answer": REFUSAL_TEXT,
            "refused": True,
            "top_score": top_score,
            "sources": []
        }

    else:

        # 4. Generate answer using retrieved documentation
        llm_start = time.perf_counter()

        try:
            answer = await generate_answer(question, chunks)

        except Exception as exc:
            logger.exception("LLM generation failed.")
            raise HTTPException(
                status_code=502,
                detail="Answer generation failed."
            ) from exc

        llm_ms = (
            time.perf_counter() - llm_start
        ) * 1000

        sources = [
            {
                "file": chunk["file"],
                "heading": chunk["heading"],
                "score": float(chunk["score"])
            }
            for chunk in chunks
        ]

        result = {
            "answer": answer,
            "refused": False,
            "top_score": top_score,
            "sources": sources
        }

    # 5. Store result in cache
    cache.set(cache_key, result)

    # 6. Calculate total latency
    latency_ms = (
        time.perf_counter() - start_time
    ) * 1000

    # 7. Log request
    await log_query({
        "ts": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "cache_hit": False,
        "refused": result["refused"],
        "top_score": top_score,
        "latency_ms": latency_ms,
        "retrieval_ms": retrieval_ms,
        "llm_ms": llm_ms
    })

    return AskResponse(
        **result,
        cached=False,
        latency_ms=latency_ms
    )