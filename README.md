# rag-eval-lab

A RAG evaluation framework built over the FastAPI documentation. It compares BM25, dense, hybrid, and reranked retrieval strategies using a manually verified evaluation dataset.

## Evaluation Dataset

The evaluation dataset contains 115 questions:

- **100 answerable questions:** Each has a verified ground-truth source file and heading.
- **15 unanswerable questions:** Designed to test whether the system can recognize queries that fall outside its knowledge base.

### Dataset Creation

- Extracted 520 eligible sections from the FastAPI documentation.
- Randomly sampled 130 sections using a fixed random seed (`42`) for reproducibility.
- Used Groq to generate one candidate question per sampled section.
- Manually reviewed all 130 generated questions.
- Retained 100 questions and rejected 30 due to weak grounding, generic wording, limited retrieval value, or insufficient support from the source section.
- Manually created 15 unanswerable questions covering topics outside the documentation corpus and checked them against the local documentation.

### Validation

The dataset was programmatically checked for:

- Exact duplicate questions.
- Missing or invalid source files.
- Missing source headings.
- Incorrect source references for unanswerable questions.

**Results:** All ground-truth references passed validation, and no exact duplicate questions were found.