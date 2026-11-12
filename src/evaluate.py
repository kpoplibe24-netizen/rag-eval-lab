import json
import argparse
from pathlib import Path

from retrieve import build_index, search
from metrics import first_correct_rank, hit_at_k, mrr


def run_eval(max_words=300, k=10, rebuild=False):

    questions = json.loads(
        Path("data/eval/questions.json").read_text(encoding="utf-8")
    )

    answerable = [q for q in questions if q["answerable"]]

    if rebuild:
        build_index(max_words)

    ranks = []
    details = []

    for q in answerable:

        results = search(q["question"], k=k, max_words=max_words)

        rank = first_correct_rank(
            results,
            q["file"],
            q["heading"]
        )

        ranks.append(rank)

        details.append({
            "question": q["question"],
            "file": q["file"],
            "heading": q["heading"],
            "rank": rank,
            "top_result": (
                f'{results[0]["file"]} | {results[0]["heading"]}'
                if results else None
            )
        })

    summary = {
        "method": "dense",
        "chunk_size": max_words,
        "n_questions": len(answerable),
        "hit@1": round(hit_at_k(ranks, 1), 4),
        "hit@3": round(hit_at_k(ranks, 3), 4),
        "hit@5": round(hit_at_k(ranks, 5), 4),
        "hit@10": round(hit_at_k(ranks, 10), 4),
        "mrr": round(mrr(ranks), 4)
    }

    return summary, details


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--chunk", type=int, default=300)
    parser.add_argument("--rebuild", action="store_true")

    args = parser.parse_args()

    summary, details = run_eval(
        max_words=args.chunk,
        rebuild=args.rebuild
    )

    print(summary)

    Path("results").mkdir(exist_ok=True)

    output = Path(f"results/dense_{args.chunk}.json")

    output.write_text(
        json.dumps({
            "summary": summary,
            "details": details
        }, indent=2),
        encoding="utf-8"
    )

    print("Saved", output)