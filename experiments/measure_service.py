import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import config

# Use a separate database for this experiment.
config.DB_PATH = str(ROOT / "logs_measure.db")

from fastapi.testclient import TestClient
import main


QUESTIONS = [
    "What is FastAPI?",
    "How do I create a FastAPI application?",
    "What is a path operation?",
    "How do I define query parameters?",
    "How do I define path parameters?",
    "How does dependency injection work in FastAPI?",
    "How do I handle request bodies?",
    "How can I return a response with a custom status code?"
]


def measure():

    uncached_times = []
    cached_times = []

    main.cache.clear()

    with TestClient(main.app) as client:

        for question in QUESTIONS:

            # First request: uncached
            first = client.post(
                "/ask",
                json={"question": question}
            )

            if first.status_code != 200:
                print(f"Skipped: {question}")
                continue

            first_data = first.json()

            if first_data["refused"]:
                print(f"Refused: {question}")
                continue

            uncached_times.append(first_data["latency_ms"])

            # Second request: cached
            second = client.post(
                "/ask",
                json={"question": question}
            )

            if second.status_code != 200:
                print(f"Cached request failed: {question}")
                continue

            second_data = second.json()

            if second_data["cached"]:
                cached_times.append(second_data["latency_ms"])

    if not uncached_times or not cached_times:
        print("Not enough successful requests to calculate latency.")
        return

    print("\nSERVICE LATENCY RESULTS")
    print("-----------------------")

    print(
        f"Uncached median: "
        f"{statistics.median(uncached_times):.2f} ms"
    )

    print(
        f"Cached median: "
        f"{statistics.median(cached_times):.2f} ms"
    )

    print(
        f"Speed improvement: "
        f"{statistics.median(uncached_times) / statistics.median(cached_times):.2f}x"
    )

    print(f"\nSuccessful uncached requests: {len(uncached_times)}")
    print(f"Successful cached requests: {len(cached_times)}")


if __name__ == "__main__":
    measure()