#!/usr/bin/env python3
"""Ingest the LangSmith / LangChain knowledge base into Chroma vector stores.

Data sources (manually collected, already in data/):
  data/documentation/  - 15 official LangSmith product docs (traces, evaluation,
                         streaming, billing, webhooks, assistants, etc.)
  data/forums/         - 15 real LangChain community forum threads from
                         forum.langchain.com covering tracing setup, deletion,
                         tool calling, streaming, rate limits, etc.
  data/blogs/          - 10 LangChain engineering blog posts covering tracing
                         philosophy, reusable evaluators, agent architecture,
                         token/agent streaming, and multi-agent patterns.

All three source types are topically aligned around the LangChain/LangSmith
ecosystem, enabling cross-source retrieval for queries about tracing, evaluation,
streaming, and agent development.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.chunkers import load_all_chunks  # noqa: E402
from src.ingestion import build_bm25_retrievers, build_vector_stores  # noqa: E402


def main() -> None:
    print("=== Step 1: Chunk documents ===")
    chunks = load_all_chunks()
    for source, docs in chunks.items():
        print(f"  {source}: {len(docs)} chunks")

    print("\n=== Step 2: Build vector stores (this may take a few minutes) ===")
    build_vector_stores(chunks)
    build_bm25_retrievers(chunks)

    print("\nIngestion complete. Run `python scripts/query.py \"your question\"` to test.")


if __name__ == "__main__":
    main()
