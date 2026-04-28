# 🎬 CineRAG

> **A Retrieval-Augmented Generation system for intelligent movie Q&A**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black"/>
  <img src="https://img.shields.io/badge/FAISS-Vector_Index-blue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Groq-Llama_3-ff6b35?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/PostgreSQL-14+-336791?style=for-the-badge&logo=postgresql&logoColor=white"/>
</p>

CineRAG is an end-to-end RAG system that answers natural language questions about movies by grounding every response in a curated knowledge base scraped from **Wikipedia** and **IMDb** — not just LLM memory. It retrieves via a dense FAISS vector index, reranks with a cross-encoder, and generates answers through Groq's Llama 3.


---

## 🔗 DEMO
<video src="https://github.com/user-attachments/assets/af1688cb-26c2-4e9d-8f83-db981060cca5" controls width="100%"></video>

---

## ✨ Core Principles

| Principle | Description |
|---|---|
| 🔍 **Groundedness** | Every answer is traceable to retrieved source chunks |
| 🛡️ **Hallucination Control** | Explicit scoring and fallback paths prevent fabrication |
| 🧠 **Query Adaptivity** | Retrieval strategy, top-k, and temperature adapt per query intent |

---

## 🏗️ Architecture

```
User Query (React UI)
        │
        ▼
  FastAPI /api/query
        │
        ▼
Intent Classification ──► Query Rewriting
        │
        ▼
 FAISS Dense Retrieval  (top-45 candidates)
        │
        ▼
Cross-Encoder Reranking  (top-9)
        │
        ▼
Movie Disambiguation & Consistency Filtering
        │
        ▼
    Adaptive Top-K Selection
        │
        ▼
Prompt Assembly ──► Groq LLM Generation
        │
        ▼
Hallucination Scoring + Confidence Scoring
        │
        ▼
  JSON Response ──► React UI
```

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| **LLM Backend** | Groq (Llama 3) |
| **Embeddings** | `BAAI/bge-large-en-v1.5` (768-dim) |
| **Vector Index** | FAISS `IndexFlatIP` (cosine similarity) |
| **Reranker** | Cross-encoder (sentence-transformers) |
| **API** | FastAPI |
| **Frontend** | React + Tailwind CSS + Vite |
| **Database** | PostgreSQL (chunk metadata store) |
| **Data Sources** | Wikipedia (scraped) + OMDB API (IMDb data) |

---

## 🗂️ Project Structure

```
cinerag/
├── data/
│   ├── movie_catalog/        ← input CSVs
│   ├── raw/                  ← scraped wiki/imdb CSVs
│   ├── inbetween/            ← cleaned, deduped, chunked CSVs
│   ├── embeddings/           ← embeddings.npy + chunks_meta.parquet
│   ├── index.faiss           ← built FAISS index
│   └── catalog.csv           ← document catalog
│
├── src/
│   ├── scraping/
│   │   └── wiki_scrap.py         ← Wikipedia scraper
│   ├── ingestion/
│   │   └── omdb_fetch.py         ← OMDB/IMDb data fetcher
│   ├── preprocessing/
│   │   ├── dedup.py              ← document builder + deduplication
│   │   └── chunker.py            ← retrieval chunker
│   ├── embedding/
│   │   ├── embedding_model.py    ← BGE model loader
│   │   ├── embedding_cache.py    ← SHA-1 embedding cache
│   │   └── embed.py              ← batch embedding runner
│   ├── indexing/
│   │   └── build_index.py        ← FAISS index builder
│   ├── retrieval/
│   │   ├── load_index.py         ← FAISS loader
│   │   ├── metadata_store.py     ← PostgreSQL chunk store
│   │   ├── retrieve.py           ← intent + query + FAISS retrieval
│   │   ├── rerank.py             ← cross-encoder reranker
│   │   └── filter_chunks.py      ← post-generation chunk filter
│   ├── llm/
│   │   ├── generate.py           ← full RAG pipeline orchestrator
│   │   ├── client.py             ← Groq API client
│   │   ├── prompt_temp.py        ← prompt builder
│   │   └── safety.py             ← answer postprocessor
│   ├── evaluation/
│   │   ├── eval.py               ← benchmark runner
│   │   ├── retrieval_metric.py   ← P@K, R@K
│   │   ├── hallucination_check.py
│   │   └── exact_match.py
│   ├── db/
│   │   └── session.py            ← SQLAlchemy engine
│   └── api/
│       ├── main.py               ← FastAPI app + routes
│       └── core/
│           └── model_store.py    ← singleton model registry
│
├── frontend/
│   ├── src/
│   │   ├── components/           ← SearchBar, AnswerCard, ContextPanel, ...
│   │   └── App.jsx
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── requirements.txt
└── package.json
```

---

## 🔄 Data Pipeline

The pipeline runs in four sequential stages before any retrieval can happen.

### Stage 1 — Wikipedia Scraping (`wiki_scrap.py`)

Reads a catalog CSV of movie titles/years, constructs Wikipedia URLs, and extracts structured HTML sections.

```
Input:  movie_catalog/final_catalog.csv  (movie_id, movie_title, title_year)
Output: raw/wiki_scrap.csv  +  raw/wiki_missing.csv
```

| Detail | Value |
|---|---|
| URL Strategy | Tries `Title` slug first, then `Title_(year_film)` fallback |
| Sections Extracted | `Plot`, `Production`, `Reception` via `h2` element IDs |
| Plot Splitting | `setup / build-up / ending` at 20% / 55% / 25% |
| Rate Limiting | Random sleep 1.2–2.5 s between requests |

Each movie produces up to 6 fields: `lead_section`, `plot_setup`, `plot_build_up`, `plot_ending`, `production`, `reception`.

---

### Stage 2 — IMDb Ingestion (`omdb_fetch.py`)

Fetches structured movie metadata from the **OMDB API** (avoids IMDb bot detection / 202 errors).

```python
# Fields fetched per movie
{
    "synopsis":    str,   # Full plot from OMDB
    "year":        str,
    "director":    str,
    "genre":       str,
    "runtime_min": int,   # Parsed from "142 min" → 142
    "language":    str,
    "country":     str,
    "imdb_rating": float, # Parsed from "8.4" → 8.4
    "awards":      str,
    "actors":      str,
}
```

```
Input:  movie_catalog/final_catalog.csv  (movie_id, movie_title, title_year, movie_imdb_id)
Output: raw/imdb_movies.csv
```

| Detail | Value |
|---|---|
| API | `https://www.omdbapi.com/` |
| Retries | 3 attempts with exponential backoff |
| Rate Limiting | 0.5–1.2 s sleep between requests; handles 429 auto-wait |
| Plot | Full plot requested (`plot=full`) |

---

### Stage 3 — Document Construction & Deduplication (`dedup.py`)

Raw Wikipedia + IMDb data is merged by `movie_id`. Each content piece becomes a standalone document:

- `imdb_synopsis` — long-form plot synopsis
- `imdb_metadata` — genre, director, cast, country, language, awards as a readable string
- Wikipedia sections → individual document records

All documents are **SHA-1 hashed** on lowercased text for exact deduplication.

```
Output: deduplicated_documents.csv
Columns: doc_id, hash_sha1, text_len, movie_id, title, year, source, section, text
```

---

### Stage 4 — Chunking, Embedding & Indexing

**Chunker** (`chunker.py`):
```
RETRIEVAL_CHUNK_SIZE  = 1200 characters (~300 tokens)
RETRIEVAL_OVERLAP_PCT = 15%  (2-sentence overlap)
RETRIEVAL_MIN_LEN     = 120 characters
```

Each chunk is prefixed with `Title: <name>\nSection: <section>` and assigned IDs like `DOC_000001_R001`.

**Embedder** (`embed.py`): Uses `BAAI/bge-large-en-v1.5` (768-dim). SHA-1 cache avoids re-encoding duplicates.

**Indexer** (`build_index.py`): Embeddings are L2-normalised → stored in `FAISS IndexFlatIP` (inner-product = cosine similarity). Metadata is stored in PostgreSQL via SQLAlchemy.

---

## 🔍 Retrieval Layer

### Intent Classification

Eight intent labels assigned via keyword heuristic cascade:

| Intent | Trigger Examples |
|---|---|
| `ending` | "ending", "final", "conclusion", "last scene" |
| `director` | "who directed", "filmmaker", "directed by" |
| `summary` | "summary", "overview", "in short" |
| `explanation` | starts with "how", "why", "explain" |
| `fact` | starts with "who", "when", "where"; "rating", "budget" |
| `character` | character/pronoun + action verb |
| `plot` | "plot", "story", "what happens" |
| `general` | fallback |

### Query Rewriting

Intent-specific keywords appended before embedding to pull toward the right semantic space:

```
plot        → "{query} plot story narrative events"
ending      → "{query} ending final scene conclusion"
director    → "{query} directed by filmmaker director"
character   → "{query} character actions role arc"
summary     → "{query} summary overview brief"
fact        → "{query} movie facts details information"
explanation → "{query} explanation reason cause effect"
```

### Section Filtering

After FAISS retrieval, chunks are filtered to intent-relevant sections:

```
director    → { imdb_metadata, lead_section, production }
fact        → { lead_section, imdb_metadata, reception }
summary     → { lead_section, imdb_synopsis }
plot        → { plot_setup, plot_build_up, plot_ending, imdb_synopsis }
ending      → { plot_ending }
explanation → { plot_build_up, plot_ending, production }
character   → { plot_*, imdb_synopsis }
general     → all sections
```

---

## ⚙️ Generation Pipeline (`generate.py`)

| Step | Description |
|---|---|
| 1 | `retrieve_by_text()` — FAISS retrieval with `k=15` |
| 2 | Detect query type via majority vote over chunk `query_type` fields |
| 3 | Cross-encoder reranks 15 chunks → top-9 selected |
| 4–6 | Score chunks per movie title; pick dominant movie (or use `extracted_movie` override) |
| 7 | Ambiguity check — if 2nd-best > 75% of top score → return ambiguity response |
| 8 | Discard chunks not from the winning movie |
| 9 | Confidence gate — if best rerank score < 0.2 → low-confidence fallback |
| 10 | Adaptive top-k selection (see below) |
| 11 | Assemble context-grounded prompt |
| 12 | Groq API call; temperature `0.05` for fact/director, `0.2` otherwise |
| 13 | `safety.postprocess_answer()` cleans output |
| 14 | `filter_supported_chunks()` keeps only entailment-supported chunks |

### Adaptive Top-K

```
fact / director    → base_k = 2
ending / plot      → base_k = 5 / 6
character / exp.   → base_k = 5
summary            → base_k = 6
general            → base_k = 5

Extension rule: include extra chunks until rerank_score drops
more than 0.25 below top chunk, or max_k = 8 reached.
```

---

## 📊 Evaluation Framework (`eval.py`)

9-query benchmark across all intent types, scored on 4 metrics:

| Metric | Definition |
|---|---|
| **Precision@5** | Fraction of top-5 chunks judged relevant by cross-encoder judge |
| **Recall@5** | Fraction of known-relevant keyword concepts found in top-5 chunks |
| **Exact Match (EM)** | Cross-encoder entailment between answer and ground truth |
| **Hallucination Rate** | Fraction of answers flagged by `hallucination_score()` |

**Answer Labels:**

- `grounded_correct` — EM passes and retrieval recall > 0
- `abstained` — model explicitly declined to answer
- `leaked_correct` — EM passes but no retrieval recall (parametric memory)
- `retrieved_but_wrong` — retrieval recall > 0 but EM fails
- `wrong_and_unsupported` — neither retrieval nor EM support the answer

---

## 🚀 Setup & Running

### Prerequisites

- Python 3.10+
- Node.js 18+ (React frontend)
- PostgreSQL 14+
- A [Groq API key](https://console.groq.com/)
- An [OMDB API key](https://www.omdbapi.com/apikey.aspx)

### Backend Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Set environment variables
export DATABASE_URL=postgresql://user:pass@localhost:5432/cinerag
export GROQ_API_KEY=your_groq_api_key
export OMDB_API_KEY=your_omdb_api_key

# 3. Run the full data pipeline (one-time setup)
python -m src.scraping.wiki_scrap
python -m src.ingestion.omdb_fetch
python -m src.preprocessing.dedup
python -m src.preprocessing.chunker
python -m src.embedding.embed
python -m src.indexing.build_index

# 4. Start the API server
uvicorn src.api.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev        # development server on :5173
npm run build      # production build → dist/
```

### Run the Evaluation Suite

```bash
python -m src.evaluation.eval

# Example output:
# Mean Precision@5:   0.782
# Mean Recall@5:      0.711
# Exact Match Rate:   0.667
# Hallucination Rate: 0.111
```

---

## 🌐 API Reference

### `POST /api/query`

```json
// Request
{
  "query": "Who directed The Godfather?",
  "max_tokens": 256
}

// Response
{
  "answer": "Francis Ford Coppola directed The Godfather.",
  "movie": "The Godfather",
  "query_type": "director",
  "confidence": 0.812,
  "context": [
    {
      "chunk_id": "DOC_000042_R001",
      "title": "The Godfather",
      "section": "imdb_metadata",
      "text": "...",
      "rerank_score": 0.91
    }
  ]
}
```

### Additional Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Liveness check → `{ "status": "ok" }` |
| `/api/movies` | GET | List all indexed movie titles |
| `/api/movie/{id}` | GET | Metadata for a single movie |

---

## 🎨 Frontend Components

| Component | Role |
|---|---|
| `SearchBar` | Free-text input with submit + loading state |
| `AnswerCard` | LLM answer, detected movie, query type badge, confidence meter |
| `ContextPanel` | Collapsible accordion of supporting chunks with section tags and rerank scores |
| `MovieBrowser` | Paginated grid of all indexed movies |
| `ErrorBanner` | Shown on ambiguous or low-confidence responses |

---

## 🧠 Key Design Decisions

<details>
<summary><b>Why FAISS IndexFlatIP instead of HNSW?</b></summary>

For a corpus of this size (tens of thousands of chunks), `IndexFlatIP` provides exact nearest-neighbour search with sub-100ms latency. HNSW trades accuracy for speed at larger scales — the accuracy loss isn't worth it here.
</details>

<details>
<summary><b>Why keyword-heuristic intent classification?</b></summary>

A lightweight rule-based classifier adds zero latency and zero API cost. For a constrained domain (movie Q&A), the heuristic covers the vast majority of query patterns. A learned classifier would require labeled training data and adds complexity without meaningful coverage gains.
</details>

<details>
<summary><b>Why separate section fields instead of one big text blob?</b></summary>

Keeping `plot_setup`, `plot_build_up`, `plot_ending`, `production`, and `reception` as separate documents allows section-level filtering during retrieval. An "ending" query can be restricted exclusively to `plot_ending` chunks, dramatically improving precision.
</details>

<details>
<summary><b>Why adaptive top-k?</b></summary>

Fixed top-k wastes context for simple fact queries (director needs 1–2 chunks) and starves complex queries (full plot summaries need 6+). Adaptive top-k uses the rerank score distribution to set the cutoff dynamically.
</details>

<details>
<summary><b>Why two-stage retrieval (FAISS → cross-encoder)?</b></summary>

FAISS bi-encoder retrieval is fast but trades precision for recall. The cross-encoder reranker reads query and chunk together, capturing fine-grained semantic overlap the bi-encoder misses. The two-stage design keeps latency acceptable while delivering reranker-quality precision.
</details>

---

## ⚠️ Known Limitations

- Wikipedia URL construction is heuristic — uncommon disambiguation patterns may miss pages
- Intent classification is rule-based — compound or ambiguous queries may be misclassified
- Single-movie per query — multi-movie comparison queries return an ambiguity response
- Groq rate limits may throttle high-concurrency deployments



## Author

**Parv Raj Chauhan**
IIIT Nagpur · CS Pre-final year

---

<p align="center">
  <i>CineRAG — Grounded answers. No hallucinations. Just movies.</i>
</p>
