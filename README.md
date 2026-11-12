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

## Retrieval Method Comparison

Four retrieval strategies were evaluated using the same 100 answerable questions to compare retrieval accuracy and ranking quality.

| Method | Chunk Size | Hit@1 | Hit@5 | Hit@10 | MRR | File Hit@5 |
|---|---:|---:|---:|---:|---:|---:|
| Dense | 100 | 0.45 | 0.73 | 0.83 | 0.5785 | 0.87 |
| Dense | 200 | 0.52 | 0.76 | 0.87 | 0.6262 | 0.88 |
| Dense | 300 | 0.51 | 0.75 | 0.85 | 0.6175 | 0.89 |
| BM25 | 200 | 0.60 | 0.84 | 0.90 | 0.6732 | 0.93 |
| Hybrid | 200 | 0.63 | 0.86 | 0.94 | 0.7312 | 0.94 |
| Reranking | 200 | **0.69** | **0.89** | **0.94** | **0.7699** | **0.95** |

### Observations

- Dense retrieval performed best with a chunk size of 200 words among the tested configurations.
- BM25 outperformed dense retrieval on this evaluation dataset.
- Hybrid retrieval improved ranking quality over both individual retrieval methods.
- Reranking achieved the highest Hit@1 and MRR, indicating better placement of relevant sections near the top of the results.
- Hybrid and reranking achieved the same Hit@10, suggesting both methods generally retrieve relevant content within their top results.

**Key takeaway:** Combining lexical and semantic retrieval, followed by CrossEncoder reranking, improved retrieval quality on this dataset. However, the additional latency of reranking must be considered.

## Confidence-Based Abstention

A retrieval system should not confidently answer questions that fall outside its knowledge base. To address this, a confidence-based abstention mechanism was implemented using the CrossEncoder reranking score.

The system compares the highest reranking score against a configurable threshold:

- If the score is greater than or equal to the threshold, the system permits answering.
- If the score is below the threshold, the system abstains.

The threshold was selected using a balanced score that considers both correct refusals and false refusals.

**Selected threshold: 3.527**

Results on the threshold-tuning dataset:

| Metric | Result |
|---|---:|
| Unanswerable questions correctly refused | 12/15 (80%) |
| Answerable questions incorrectly refused | 15/100 (15%) |
| Answerable questions allowed | 85/100 (85%) |
| Unanswerable questions incorrectly allowed | 3/15 (20%) |
| Balanced score | 0.825 |

The threshold is model- and dataset-specific. CrossEncoder scores are not calibrated probabilities, so the selected value should not be assumed to generalize to other datasets