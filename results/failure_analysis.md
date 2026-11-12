# Failure Analysis

## Category Breakdown

| Category | Count |
|---|---:|
| Near-miss (right page, wrong section) | 10 |
| Term collision | 2 |
| Vocabulary mismatch | 1 |
| Weak question | 1 |
| Thin section | 0 |
| **Total** | **14** |

## Observations

Most failures were near-misses, where retrieval found related documentation but ranked the expected section below the top five. For example, the question about streaming JSON objects retrieved other sections from the same JSON Lines documentation page.

Term collisions also affected retrieval. For example, the question about starting a minimal FastAPI application retrieved sections about proxy configuration, while the password-filtering question retrieved security sections mentioning passwords.

One question had a vocabulary mismatch: the question about Pydantic validation formats was not retrieved accurately despite the expected section discussing validation and supported data types.

The weak-question category highlights that some questions may not clearly identify a specific section. These findings show that retrieval failures are caused by a combination of ranking limitations, overlapping terminology, and question quality.

## Out-of-Scope Near-Misses

Two examples from the threshold evaluation demonstrate limitations in refusing unrelated questions:

- **Heroku:** Matched `Deploy your app (optional)`, a FastAPI Cloud page, with a reranker score of 5.63.
- **Celery:** Matched a background-tasks caveat that mentions Celery in passing.

These examples show that keyword or topical overlap can produce high retrieval scores even when the retrieved content does not answer the question.