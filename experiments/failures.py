import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from make_questions import eligible_sections
from methods import hybrid_search

lookup = {(s["file"], s["heading"]): s["text"] for s in eligible_sections()}
details = json.loads(Path("results/hybrid_200.json").read_text(encoding="utf-8"))["details"]

# Failures = correct section not in the top 5
failures = [d for d in details if d["rank"] is None or d["rank"] > 5]
print("hit@5 failures:", len(failures))

lines = [f"# Failure worksheet ({len(failures)} questions)\n"]
for n, d in enumerate(failures, start=1):
    top3 = hybrid_search(d["question"], k=3, max_words=200)
    lines.append(f"## {n}. {d['question']}")
    lines.append(f"- Expected: `{d['file']} | {d['heading']}` (rank: {d['rank']})")
    for i, r in enumerate(top3, start=1):
        lines.append(f"- Got #{i}: `{r['file']} | {r['heading']}`")
    expected_text = lookup.get((d["file"], d["heading"]), "")[:500].replace("\n", " ")
    lines.append(f"- Expected section starts: {expected_text}")
    lines.append("- **Category:** ")
    lines.append("")

Path("results/failures_worksheet.md").write_text("\n".join(lines), encoding="utf-8")
print("Wrote results/failures_worksheet.md")