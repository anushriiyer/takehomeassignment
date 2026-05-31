# Multi-Source RAG — LangSmith / LangChain Support

A RAG system that answers questions about LangSmith and the LangChain ecosystem by pulling from three real knowledge sources: official docs, community forum threads, and engineering blog posts.

| Source | Count | Format | Chunking |
|--------|-------|--------|----------|
| Documentation | 15 pages | Markdown | Header-based (`MarkdownHeaderTextSplitter`) |
| Community Forums | 15 threads | JSON | Per-post with author role in metadata |
| Blog Posts | 10 articles | Markdown | Paragraph-level with overlap |

## How it works

```
Query
  │
  ▼
Weighted Multi-Source Retriever
  vector (Chroma) + BM25 per source
  docs: 1.0  blogs: 0.85  forums: 0.65
  │
  ▼
Cross-Encoder Reranker
  ms-marco-MiniLM-L6-v2, top-24 → top-5
  │
  ▼
Contradiction Detector
  regex claim extraction, authority: docs > blogs > forums
  │
  ▼
LLM Generation (Gemini 2.5 Flash)
  │
  ▼
Answer + structured log
```

The retrieval and reranking run entirely locally (no API needed). The LLM is only used for final answer synthesis.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Add your Gemini key
echo "GOOGLE_API_KEY=your_key_here" > .env

# Build the vector store (one-time, ~2 min)
python scripts/ingest.py

# Ask a question
python scripts/query.py "How do I enable LangSmith tracing?"

# Run all 15 example queries
python scripts/run_examples.py

# Retrieval/reranking benchmark
python scripts/benchmark.py
```

## Project structure

```
data/
  documentation/    15 LangSmith docs (.md)
  forums/           15 forum threads (.json)
  blogs/            10 blog posts (.md)
src/
  chunkers.py       source-specific splitting strategies
  ingestion.py      Chroma collections + BM25 setup
  retrieval.py      weighted multi-source retriever
  reranker.py       cross-encoder reranking
  contradiction.py  cross-source conflict detection
  logging_utils.py  structured per-query logging
  pipeline.py       end-to-end pipeline
scripts/
  ingest.py         index all sources into Chroma
  query.py          single query CLI
  run_examples.py   run 15 example queries
  benchmark.py      precision@5 before/after reranking
examples/
  example_results.json       query outputs
  performance_analysis.json  benchmark results
logs/                per-query JSON logs
QueryResults.md            full writeup
```

## Performance (measured)

| | Pre-rerank | Post-rerank |
|---|:---:|:---:|
| Precision@5 | 0.45 | **0.92** |
| Retrieval latency | 167ms | — |
| Reranking latency | — | 1,605ms |

Full breakdown in [REPORT.md](REPORT.md).

## Requirements

- Python 3.10+
- ~2 GB disk for local embedding and reranker models (downloaded on first run)
- Gemini API key for answer synthesis (retrieval works without it)
