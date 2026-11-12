import json
from pathlib import Path

with open("data/eval/questions.json", encoding="utf-8") as f:
    questions = json.load(f)

docs_dir = Path("data/docs")

errors = []

for i, item in enumerate(questions, start=1):

    if item["answerable"]:
        if not item["file"] or not item["heading"]:
            errors.append(f"Question {i}: Missing file or heading")
            continue

        path = docs_dir / item["file"]

        if not path.exists():
            errors.append(f"Question {i}: File does not exist: {item['file']}")
            continue

        text = path.read_text(encoding="utf-8")

        if item["heading"] not in text:
            errors.append(
                f"Question {i}: Heading not found in {item['file']}: "
                f"{item['heading']}"
            )

    else:
        if item["file"] is not None or item["heading"] is not None:
            errors.append(f"Question {i}: Unanswerable question has a source")

if errors:
    print("Validation errors:")
    for error in errors:
        print(error)
else:
    print("All ground-truth references are valid!")