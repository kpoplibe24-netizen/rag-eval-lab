import json
import os
from pathlib import Path

MAX_WORDS = 200
TOP_K = 4

CACHE_TTL_SECONDS = 3600
CACHE_MAX_ITEMS = 500

DB_PATH = os.environ.get("DB_PATH", "logs.db")

LLM_MODEL = os.environ.get(
    "LLM_MODEL",
    "openai/gpt-oss-120b"
)


def load_threshold() -> float:

    if "REFUSAL_THRESHOLD" in os.environ:
        return float(os.environ["REFUSAL_THRESHOLD"])

    path = Path("results/chosen_threshold.json")

    if not path.exists():
        raise RuntimeError(
            "results/chosen_threshold.json not found."
        )

    return float(
        json.loads(path.read_text(encoding="utf-8"))["threshold"]
    )