import json
import sys

def load(name):
    d = json.load(open(f"results/{name}.json", encoding="utf-8"))["details"]
    return {x["question"]: x["rank"] for x in d}

a, b = load(sys.argv[1]), load(sys.argv[2])
inf = 99  # "not found" counts as a very bad rank

wins = sum(1 for q in a if (b[q] or inf) < (a[q] or inf))
losses = sum(1 for q in a if (b[q] or inf) > (a[q] or inf))
print(f"{sys.argv[2]} vs {sys.argv[1]}: better on {wins}, worse on {losses}, same on {len(a) - wins - losses}")