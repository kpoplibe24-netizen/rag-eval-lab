import sqlite3

import config
import db


def test_init_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", str(db_path))

    db.init_db()

    conn = sqlite3.connect(db_path)

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )

    tables = [row[0] for row in cursor.fetchall()]

    conn.close()

    assert "query_log" in tables


def test_log_query(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", str(db_path))

    db.init_db()

    row = {
        "ts": "2026-11-13T10:00:00+00:00",
        "question": "What is FastAPI?",
        "cache_hit": False,
        "refused": False,
        "top_score": 4.5,
        "latency_ms": 120.5,
        "retrieval_ms": 30.2,
        "llm_ms": 90.3
    }

    db.log_query(row)

    conn = sqlite3.connect(db_path)
    result = conn.execute(
        "SELECT question, cache_hit, refused FROM query_log"
    ).fetchone()
    conn.close()

    assert result == ("What is FastAPI?", 0, 0)


def test_get_stats(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", str(db_path))

    db.init_db()

    rows = [
        {
            "ts": "2026-11-13T10:00:00+00:00",
            "question": "Question 1",
            "cache_hit": False,
            "refused": False,
            "top_score": 4.5,
            "latency_ms": 120.0,
            "retrieval_ms": 30.0,
            "llm_ms": 90.0
        },
        {
            "ts": "2026-11-13T10:01:00+00:00",
            "question": "Question 2",
            "cache_hit": True,
            "refused": False,
            "top_score": 4.5,
            "latency_ms": 2.0,
            "retrieval_ms": 0.0,
            "llm_ms": 0.0
        },
        {
            "ts": "2026-11-13T10:02:00+00:00",
            "question": "Question 3",
            "cache_hit": False,
            "refused": True,
            "top_score": 1.0,
            "latency_ms": 35.0,
            "retrieval_ms": 35.0,
            "llm_ms": 0.0
        }
    ]

    for row in rows:
        db.log_query(row)

    stats = db.get_stats()

    assert stats["overall"]["total_queries"] == 3
    assert stats["overall"]["cache_hit_pct"] == 33.33
    assert stats["overall"]["refused_pct"] == 33.33
    assert len(stats["latency_answered"]) == 2