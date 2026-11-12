# RetrievalForge

![CI](https://github.com/kpoplibe24-netizen/retrieval_forge/actions/workflows/eval.yml/badge.svg)

A retrieval evaluation lab and QA service over the FastAPI documentation.

It compares dense, BM25, hybrid and reranked retrieval on a hand-reviewed question set, then serves the pipeline through an async FastAPI app.

## Results

100 answerable questions, strict match on file + section heading (chunk size 200 words).

| Method | hit@1 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|
| Dense (MiniLM) | 0.52 | 0.76 | 0.87 | 0.626 |
| BM25 | 0.56 | 0.84 | 0.90 | 0.673 |
| Hybrid (RRF) | 0.63 | 0.86 | 0.94 | 0.731 |
| Hybrid + cross-encoder rerank | 0.69 | 0.89 | 0.94 | 0.770 |

Chunk size (100/200/300 words, dense only) made little difference.

Full table: `results/ablation.md`.

### Findings

- Hybrid achieved Hit@5 of 0.86 compared with 0.76 for dense retrieval.
- BM25 was competitive with dense retrieval, plausibly because the documentation contains exact identifiers like `Depends` and `UploadFile`.
- Reranking improved Hit@1 from 0.63 to 0.69 and MRR from 0.731 to 0.770.
- Failure analysis identified near-misses, term collisions, vocabulary mismatches and weak questions. See `results/failure_analysis.md`.

### Refusing out-of-scope questions

Questions whose best reranker score is below a threshold (3.527) are refused without calling the LLM.

On 15 hand-written out-of-scope questions, 12 were refused, and 15 of 100 in-scope questions were wrongly refused.

The threshold was chosen on these same questions, so the numbers are optimistic.

## Service

- `POST /ask`: answer with sources, `refused`, `cached`, `latency_ms`
- `GET /health`, `GET /stats` (SQL aggregates over the query log)
- Async handlers; CPU-bound retrieval runs in a worker thread
- In-memory TTL cache: median 2188.67 ms uncached vs 0.03 ms cached (median of 8 questions, one laptop)
- SQLite query log (`sql/analytics.sql`)
- 20 pytest tests; CI also fails if hybrid Hit@5 or MRR drops below the baseline

## How the evaluation set was made

130 sections were sampled at random (seed 42) from sections with at least 40 words of real text.

An LLM drafted questions, using Gemini for the first 15 and Groq `gpt-oss-120b` for the rest. Every retained question was manually reviewed.

The final evaluation set contains 100 answerable questions and 15 hand-written out-of-scope questions.

The 15 out-of-scope questions were checked against the documentation by keyword search.

## Run it

```bash
pip install -r requirements.txt
python src/retrieve.py
python src/evaluate.py --method hybrid --chunk 200
```

Set your Groq API key in PowerShell:

```powershell
$env:GROQ_API_KEY="..."
```

Start the API:

```bash
uvicorn main:app --app-dir src --port 8000
```

## Limitations

- One test set of 100 answerable questions, drafted from the section text, which may favor keyword methods.
- Strict section matching counts near-misses on the right page as failures.
- The cache is per-process and lost on restart.
- Answer quality from the LLM is not evaluated, only retrieval.
- The refusal threshold was selected and evaluated on the same dataset, making the reported refusal performance optimistic.

## Data

Documentation text from the FastAPI project (MIT licensed): https://github.com/fastapi/fastapi