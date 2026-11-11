from dataclasses import dataclass
from pathlib import Path
import random
from collections import Counter
import re

@dataclass
class Chunk:
    chunk_id: str
    file: str
    heading: str
    text: str


def split_by_headings(markdown_text: str):
    sections = []

    current_heading = "INTRO"
    current_lines = []

    in_code_block = False

    for line in markdown_text.splitlines():

        if line.strip().startswith("```"):
            in_code_block = not in_code_block

        if not in_code_block and line.startswith("#"):
            if current_lines:
                sections.append(
                    (current_heading, "\n".join(current_lines))
                )

            current_heading = line.lstrip("#").strip()
            current_heading = re.sub(r"\s*\{\s*#[^}]*\}\s*$", "", current_heading).strip()
            current_lines = []

        else:
            current_lines.append(line)

    if current_lines:
        sections.append(
            (current_heading, "\n".join(current_lines))
        )

    return sections


def split_long_section(text: str, max_words: int):
    words = text.split()

    chunks = []

    for i in range(0, len(words), max_words):
        piece = " ".join(words[i:i + max_words])
        chunks.append(piece)

    return chunks


def build_chunks(docs_dir: str, max_words: int):
    chunks = []

    docs_path = Path(docs_dir)

    for path in sorted(docs_path.rglob("*.md")):

        text = path.read_text(encoding="utf-8")

        relative_path = path.relative_to(docs_path).as_posix()

        sections = split_by_headings(text)

        for heading, section_text in sections:

            if not section_text.strip():
                continue

            pieces = split_long_section(section_text, max_words)

            for i, piece in enumerate(pieces):

                chunk = Chunk(
                    chunk_id=f"{relative_path}::{heading}::{i}",
                    file=relative_path,
                    heading=heading,
                    text=f"{heading}\n{piece}"
                )

                chunks.append(chunk)

    return chunks


if __name__ == "__main__":

    chunks = build_chunks("data/docs", max_words=300)

    print("Total chunks:", len(chunks))

    for chunk in random.sample(chunks, min(5, len(chunks))):

        print("\n----------------------------")
        print("ID:", chunk.chunk_id)
        print("FILE:", chunk.file)
        print("HEADING:", chunk.heading)
        print("TEXT:", chunk.text[:500])