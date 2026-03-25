# Movie Trivia RAG Chatbot

> A production-oriented Retrieval-Augmented Generation system for factual movie Q&A — built around correctness, evaluation, and real-world ambiguity handling.

---

## Overview

Most LLM-based Q&A systems hallucinate when pushed beyond their training distribution. This project takes a different approach: instead of relying on an LLM's internal knowledge, every answer is grounded in retrieved context from a structured movie dataset.

Ask it anything:

```
Who directed Inception?
Which Spider-Man movie had Venom?
Who acted in Interstellar?
```

The system retrieves, reranks, aggregates, and only then generates — minimizing hallucination at every stage.

---

## Architecture

```
User Query
    │
    ▼
Query Embedding          (sentence-transformers)
    │
    ▼
Vector Retrieval         (FAISS, Top-K cosine similarity)
    │
    ▼
Reranking + Aggregation  (score aggregation per movie title)
    │
    ▼
Context Selection        (top-ranked movie context only)
    │
    ▼
LLM Generation           (grounded, context-constrained)
    │
    ▼
Final Answer
```

---

## Key Design Decisions

### Section-Aware Chunking

Movie data is split into typed chunks — `title`, `cast`, `director`, `plot` — rather than ingested as flat documents. This improves retrieval precision by letting the reranker score sections independently and surface the most relevant field per query.

### Movie-Level Aggregation

Retrieved chunks are grouped by movie title before generation. Relevance scores are summed per movie, and the highest-scoring movie's full context is passed to the LLM. This eliminates a common failure mode: mixing cast or plot details from multiple films in a single answer.

### Constrained Generation

The LLM is prompted strictly from retrieved context. It is not allowed to supplement with parametric knowledge. This trades recall on obscure queries for a hard guarantee against hallucination on known ones.

---

## Evaluation

The system uses explicit retrieval metrics rather than subjective output quality:

| Metric | Description |
|---|---|
| Precision@K | Fraction of top-K retrieved chunks that are relevant |
| Recall@K | Fraction of relevant chunks captured in top-K |
| Answer label | `Correct` / `Hallucinated` — manually annotated |

**Example:**

```
Query:      Who directed Inception?
Answer:     Christopher Nolan
P@5:        0.50
R@5:        1.00
Label:      Correct ✓
```

Evaluation is used to guide architectural changes, not just report results.

---

## Known Limitations

These are documented intentionally — known failures are more useful than hidden ones.

| Issue | Cause | Status |
|---|---|---|
| Generic movie titles (`Her`, `Up`) | Ambiguous retrieval | Open |
| Franchise queries (`Who played Spider-Man?`) | Multi-movie score mixing | Open |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Embeddings | `sentence-transformers` |
| Vector store | FAISS |
| Generation | Groq |
| Frontend | Next.js |

---

## Project Structure

```
movie-rag-chatbot/
├── data/
│   └── movie_documents/     # raw and chunked movie data
├── embeddings/              # embedding generation scripts
├── retrieval/               # FAISS index + search logic
├── reranking/               # score aggregation + context selection
├── evaluation/              # Precision@K, Recall@K, labeling
├── api/                     # FastAPI app (planned)
├── frontend/                # Next.js UI (planned)
├── main.py
├── requirements.txt
└── README.md
```

---

## Setup

**1. Clone and enter the repo**

```bash
git clone <your-repo-url>
cd movie-rag-chatbot
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
cd frontend && npm install
```

**4. Run the pipeline**

```bash
python main.py
```

---

## Design Philosophy

This project prioritizes correctness over feature count. Specifically:

- **Known limitations over hidden failures** — every edge case is documented, not papered over
- **Evaluation-driven development** — changes are validated with metrics, not vibes
- **Minimal abstraction in v1** — no agent frameworks, no heavy orchestration; the pipeline is readable end-to-end
- **Grounded generation** — the LLM is a synthesizer, not a knowledge source

---

## Roadmap

**v2 planned improvements:**

- [ ] Named entity recognition for movie disambiguation
- [ ] Improved franchise handling (per-installment scoring)
- [ ] FastAPI backend with documented endpoints
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Optional LangChain orchestration layer

---

## Author

**Parv Raj Chauhan**
