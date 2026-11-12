import json
from pathlib import Path
from make_questions import eligible_sections

# Read LLM-drafted questions
cands = json.loads(
    Path("data/eval/candidates.json").read_text(encoding="utf-8")
)

# Lookup of documentation sections
lookup = {
    (s["file"], s["heading"]): s["text"]
    for s in eligible_sections()
}

out_path = Path("data/eval/questions.json")
rej_path = Path("data/eval/rejected.json")

kept = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else []
rejected = json.loads(rej_path.read_text(encoding="utf-8")) if rej_path.exists() else []

# Sections already reviewed (kept OR deleted)
done = {(k["file"], k["heading"]) for k in kept}
done |= {(r["file"], r["heading"]) for r in rejected}

todo = [c for c in cands if (c["file"], c["heading"]) not in done]
print(f"To review: {len(todo)} | kept: {len(kept)} | deleted: {len(rejected)}")

for n, c in enumerate(todo, start=1):

    print("\n" + "=" * 70)
    print(f"[{n}/{len(todo)}]")
    print("SECTION:", c["file"], "|", c["heading"])
    print(lookup[(c["file"], c["heading"])][:900])
    print("\nQUESTION:", c["question"])

    choice = input("[Enter]=keep  e=edit  d=delete  q=quit > ").strip().lower()

    if choice == "q":
        break

    if choice == "d":
        rejected.append(c)
        rej_path.write_text(json.dumps(rejected, indent=2), encoding="utf-8")
        continue

    if choice == "e":
        new_q = input("New question: ").strip()
        if new_q:
            c["question"] = new_q

    kept.append(c)
    out_path.write_text(json.dumps(kept, indent=2), encoding="utf-8")

print(f"\nKept: {len(kept)} | Deleted: {len(rejected)}")