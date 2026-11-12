import os
import json
import random
import re
import time

from pathlib import Path
from ingest import split_by_headings


MODEL_NAME = "openai/gpt-oss-120b"   # if this errors, pick a current model name from Groq's model list
BATCH = 6


# Clean documentation text
def real_text(section_text: str) -> str:
    t = re.sub(r"```.*?```", "", section_text, flags=re.DOTALL)
    t = re.sub(r"\{\*.*?\*\}", "", t, flags=re.DOTALL)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"!\[.*?\]\(.*?\)", "", t)

    return t.strip()


# Ignore generic sections
GENERIC = {
    "recap",
    "check it",
    "intro",
    "review",
    "recap again",
    "technical details"
}


# Find eligible sections
def eligible_sections(docs_dir="data/docs", min_words=40):
    docs = Path(docs_dir)
    out = []

    for path in sorted(docs.rglob("*.md")):
        rel = path.relative_to(docs).as_posix()

        text = path.read_text(encoding="utf-8")
        sections = split_by_headings(text)

        for heading, body in sections:
            clean = real_text(body)

            if (
                len(clean.split()) >= min_words
                and heading.lower() not in GENERIC
            ):
                out.append({
                    "file": rel,
                    "heading": heading,
                    "text": clean
                })

    return out


# Question-generation prompt (several sections per call)
PROMPT = """You are helping build a test set for a documentation search system.

Below are {n} sections of the FastAPI documentation, numbered 0 to {last}.

For EACH section, write ONE question a developer might type into a search box
that this section answers.

Rules:
- The question must be answerable using ONLY that section.
- Do NOT copy the section heading's words directly.
- Rephrase the question naturally.
- Return ONLY a JSON list of {n} strings, in the same order as the sections.
- No extra text, no explanations.

{body}
"""


# Main execution
if __name__ == "__main__":
    from groq import Groq

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    sections = eligible_sections()
    print(f"Eligible sections found: {len(sections)}")

    random.seed(42)
    sample = random.sample(sections, min(130, len(sections)))

    # Output file
    output_path = Path("data/eval/candidates.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load previously generated candidates
    if output_path.exists():
        candidates = json.loads(output_path.read_text(encoding="utf-8"))
    else:
        candidates = []

    # Sections already processed
    done = {(c["file"], c["heading"]) for c in candidates}

    todo = [s for s in sample if (s["file"], s["heading"]) not in done]

    print(f"Already generated: {len(candidates)}")
    print(f"Remaining sections: {len(todo)}")

    failures_in_a_row = 0

    for i in range(0, len(todo), BATCH):
        group = todo[i:i + BATCH]

        body = "\n\n".join(
            f"### Section {j}\nHeading: {s['heading']}\n{s['text'][:1500]}"
            for j, s in enumerate(group)
        )

        prompt = PROMPT.format(n=len(group), last=len(group) - 1, body=body)

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content or ""
            match = re.search(r"\[.*\]", text, re.DOTALL)
            questions = json.loads(match.group(0))
            assert len(questions) == len(group)

        except Exception as e:
            print(f"\nProblem at batch {i // BATCH + 1}: {e}")
            failures_in_a_row += 1
            if failures_in_a_row >= 3:
                print("3 failures in a row. Stopping. Everything so far is saved; rerun later.")
                break
            time.sleep(15)
            continue

        failures_in_a_row = 0

        for s, q in zip(group, questions):
            candidates.append({
                "file": s["file"],
                "heading": s["heading"],
                "question": str(q).strip(),
                "answerable": True
            })

        # Save after every successful batch
        output_path.write_text(
            json.dumps(candidates, indent=4),
            encoding="utf-8"
        )

        print(f"Total candidates: {len(candidates)}")

        # Wait to avoid exceeding rate limits
        time.sleep(5)

    print(f"\nSaved {len(candidates)} questions to {output_path}")