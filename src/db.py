import sqlite3
from datetime import datetime, timezone

import config


def get_connection():
    return sqlite3.connect(config.DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS query_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                question TEXT NOT NULL,
                cache_hit INTEGER NOT NULL,
                refused INTEGER NOT NULL,
                top_score REAL,
                latency_ms REAL,
                retrieval_ms REAL,
                llm_ms REAL
            )
        """)


def log_query(row):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO query_log (
                ts,
                question,
                cache_hit,
                refused,
                top_score,
                latency_ms,
                retrieval_ms,
                llm_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["ts"],
            row["question"],
            int(row["cache_hit"]),
            int(row["refused"]),
            row["top_score"],
            row["latency_ms"],
            row["retrieval_ms"],
            row["llm_ms"]
        ))


def get_stats():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row

        overall = conn.execute("""
            SELECT
                COUNT(*) AS total_queries,
                ROUND(100.0 * AVG(cache_hit), 2) AS cache_hit_pct,
                ROUND(100.0 * AVG(refused), 2) AS refused_pct
            FROM query_log
        """).fetchone()

        latency_answered = conn.execute("""
            SELECT
                cache_hit,
                COUNT(*) AS count,
                ROUND(AVG(latency_ms), 2) AS avg_latency_ms
            FROM query_log
            WHERE refused = 0
            GROUP BY cache_hit
        """).fetchall()

    return {
        "overall": dict(overall),
        "latency_answered": [
            dict(row) for row in latency_answered
        ]
    }