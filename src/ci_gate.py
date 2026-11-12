import json
import sys
from pathlib import Path

from retrieve import build_index
from evaluate import run_eval

BASELINE = Path("results/baseline.json")
TOLERANCE = 0.03
GATED = ["hit@5", "mrr"]
CHUNK = 200

if __name__ == "__main__":
    build_index(CHUNK)
    summary, _ = run_eval("hybrid", CHUNK)
    current = {m: summary[m] for m in GATED}
    print("current: ", current)

    if "--update" in sys.argv:
        BASELINE.write_text(json.dumps(current, indent=2), encoding="utf-8")
        print("baseline saved to", BASELINE)
        sys.exit(0)

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    print("baseline:", baseline)

    failed = [m for m in GATED if current[m] < baseline[m] - TOLERANCE]
    if failed:
        print(f"FAIL: regression in {failed} (tolerance {TOLERANCE})")
        sys.exit(1)
    print("PASS: retrieval quality is within tolerance of the baseline")