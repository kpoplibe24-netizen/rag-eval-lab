import sys
import json
from pathlib import Path

from methods import rerank_search

SCORES_PATH = Path("results/threshold_scores.json")


def compute_scores():
    questions = json.loads(Path("data/eval/questions.json").read_text(encoding="utf-8"))
    n_un = sum(1 for q in questions if not q["answerable"])
    assert n_un > 0, "No unanswerable questions found. Add them first."

    scores = []
    for i, q in enumerate(questions, start=1):
        top = rerank_search(q["question"], k=1, max_words=200)[0]
        scores.append({
            "question": q["question"],
            "answerable": q["answerable"],
            "top_score": top["score"],
            "top_result": f'{top["file"]} | {top["heading"]}',
        })
        if i % 20 == 0:
            print(f"scored {i}/{len(questions)}")

    Path("results").mkdir(exist_ok=True)
    SCORES_PATH.write_text(json.dumps(scores, indent=2), encoding="utf-8")
    return scores


def rates(scores, t):
    ans = [s for s in scores if s["answerable"]]
    unans = [s for s in scores if not s["answerable"]]
    refused_un = sum(1 for s in unans if s["top_score"] < t)
    refused_ans = sum(1 for s in ans if s["top_score"] < t)
    return refused_un, len(unans), refused_ans, len(ans)


if __name__ == "__main__":
    # Scores are cached, so trying a different threshold is instant.
    if SCORES_PATH.exists() and "--refresh" not in sys.argv:
        scores = json.loads(SCORES_PATH.read_text(encoding="utf-8"))
    else:
        scores = compute_scores()

    ans = sorted(s["top_score"] for s in scores if s["answerable"])
    unans = sorted(s["top_score"] for s in scores if not s["answerable"])
    print(f"answerable: {len(ans)} | unanswerable: {len(unans)}")
    print(f"mean top score  answerable: {sum(ans)/len(ans):.2f} | unanswerable: {sum(unans)/len(unans):.2f}")

    # If you pass a number, report just that threshold and stop.
    nums = [a for a in sys.argv[1:] if not a.startswith("--")]
    if nums:
        t = float(nums[0])
        ru, nu, ra, na = rates(scores, t)
        print(f"\nThreshold {t}: refused {ru}/{nu} unanswerable, wrongly refused {ra}/{na} answerable")
        sys.exit()

    # Otherwise sweep thresholds across the range of scores seen.
    lo, hi = min(ans + unans), max(ans + unans)
    sweep = []
    for i in range(41):
        t = lo + (hi - lo) * i / 40
        ru, nu, ra, na = rates(scores, t)
        sweep.append({"threshold": round(t, 3),
                      "correct_refusal": round(ru / nu, 3),
                      "false_refusal": round(ra / na, 3),
                      "balanced": round((ru / nu + (1 - ra / na)) / 2, 3)})

    print("\nthreshold | correct refusals | false refusals")
    for r in sweep[::3]:
        print(f'{r["threshold"]:9} | {r["correct_refusal"]:16} | {r["false_refusal"]:14}')

    best = max(sweep, key=lambda r: r["balanced"])
    print("\nBest balanced threshold:", best)

    print("\nUnanswerable questions with the HIGHEST scores (would sneak through):")
    for s in sorted([s for s in scores if not s["answerable"]], key=lambda s: -s["top_score"])[:5]:
        print(f'  {s["top_score"]:.2f}  {s["question"]}  ->  {s["top_result"]}')

    print("\nAnswerable questions with the LOWEST scores (would be wrongly refused):")
    for s in sorted([s for s in scores if s["answerable"]], key=lambda s: s["top_score"])[:5]:
        print(f'  {s["top_score"]:.2f}  {s["question"]}  ->  {s["top_result"]}')

    Path("results/threshold.json").write_text(
        json.dumps({"best_balanced": best, "sweep": sweep}, indent=2), encoding="utf-8")