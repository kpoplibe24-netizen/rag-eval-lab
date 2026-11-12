import json
from pathlib import Path

rows = []

for p in Path("results").glob("*.json"):
    data = json.loads(p.read_text(encoding="utf-8"))

    if "summary" in data:
        rows.append(data["summary"])


order = {
    "dense": 0,
    "bm25": 1,
    "hybrid": 2,
    "rerank": 3
}

rows.sort(
    key=lambda s: (order.get(s["method"], 9), s["chunk_size"])
)


lines = [
    "| Method | Chunk | hit@1 | hit@5 | hit@10 | MRR | file hit@5 |",
    "|---|---|---|---|---|---|---|"
]

for s in rows:
    lines.append(
        f'| {s["method"]} | {s["chunk_size"]} | {s["hit@1"]} | '
        f'{s["hit@5"]} | {s["hit@10"]} | {s["mrr"]} | '
        f'{s.get("file_hit@5", "-")} |'
    )


Path("results/ablation.md").write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print("\n".join(lines))