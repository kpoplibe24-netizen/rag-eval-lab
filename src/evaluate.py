import json
import argparse
from pathlib import Path

from retrieve import build_index, search as dense_search
from methods import bm25_search, hybrid_search, rerank_search
from metrics import first_correct_rank, hit_at_k, mrr


METHODS = {
    "dense": dense_search,
    "bm25": bm25_search,
    "hybrid": hybrid_search,
    "rerank": rerank_search,
}


def first_file_rank(results, file):
    for i, r in enumerate(results, start=1):
        if r["file"] == file:
            return i
    return None


def run_eval(method="dense", max_words=300, k=10):
    search_fn = METHODS[method]

    questions = json.loads(
        Path("data/eval/questions.json").read_text(encoding="utf-8")
    )

    answerable = [q for q in questions if q["answerable"]]

    ranks, file_ranks, details = [], [], []

    for q in answerable:
        results = search_fn(
            q["question"],
            k=k,
            max_words=max_words
        )

        rank = first_correct_rank(
            results,
            q["file"],
            q["heading"]
        )

        ranks.append(rank)
        file_ranks.append(first_file_rank(results, q["file"]))

        details.append({
            "question": q["question"],
            "file": q["file"],
            "heading": q["heading"],
            "rank": rank,
            "top_result": (
                f'{results[0]["file"]} | {results[0]["heading"]}'
                if results else None
            ),
        })

    summary = {
        "method": method,
        "chunk_size": max_words,
        "n_questions": len(answerable),
        "hit@1": round(hit_at_k(ranks, 1), 4),
        "hit@3": round(hit_at_k(ranks, 3), 4),
        "hit@5": round(hit_at_k(ranks, 5), 4),
        "hit@10": round(hit_at_k(ranks, 10), 4),
        "mrr": round(mrr(ranks), 4),
        "file_hit@5": round(hit_at_k(file_ranks, 5), 4),
    }

    return summary, details


if __name__ == "__main__":
    p = argparse.ArgumentParser()

    p.add_argument(
        "--method",
        default="dense",
        choices=list(METHODS)
    )

    p.add_argument("--chunk", type=int, default=300)
    p.add_argument("--rebuild", action="store_true")

    args = p.parse_args()

    if args.rebuild:
        build_index(args.chunk)

    summary, details = run_eval(args.method, args.chunk)

    print(summary)

    Path("results").mkdir(exist_ok=True)

    out = Path(f"results/{args.method}_{args.chunk}.json")

    out.write_text(
        json.dumps({
            "summary": summary,
            "details": details
        }, indent=2),
        encoding="utf-8"
    )

    print("Saved", out)