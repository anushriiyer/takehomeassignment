"""Configuration for the LangSmith multi-source RAG system.

Knowledge base covers the LangChain / LangSmith ecosystem:
  - documentation/  : Official LangSmith product docs (traces, evaluation, billing, streaming, webhooks)
  - forums/         : LangChain community forum threads (real user Q&A from forum.langchain.com)
  - blogs/          : LangChain engineering blog posts (agent architecture, tracing philosophy, evaluators)

Source weights reflect trust/authority:
  documentation > blog > forum
The cross-encoder reranker can override this ordering for individual queries,
but the weight pre-filters coarser results before reranking begins.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
CHROMA_DIR = ROOT_DIR / "chroma_db"
LOGS_DIR = ROOT_DIR / "logs"

DOCUMENTATION_DIR = DATA_DIR / "documentation"
FORUMS_DIR = DATA_DIR / "forums"
BLOGS_DIR = DATA_DIR / "blogs"

# Source trust weights for retrieval fusion (higher = more preferred in pre-rerank scoring)
SOURCE_WEIGHTS: dict[str, float] = {
    "documentation": 1.0,   # Official product docs — versioned, authoritative
    "blog": 0.85,            # Engineering blog — team-authored, may lag docs slightly
    "forum": 0.65,           # Community Q&A — practical workarounds, may be outdated
}

# Authority order for contradiction resolution (highest first)
SOURCE_AUTHORITY: list[str] = ["documentation", "blog", "forum"]

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L6-v2")

RETRIEVAL_K_PER_SOURCE = int(os.getenv("RETRIEVAL_K_PER_SOURCE", "8"))
RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", "5"))
FINAL_CONTEXT_K = int(os.getenv("FINAL_CONTEXT_K", "5"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

COLLECTION_NAMES = {
    "documentation": "langsmith_docs",
    "forum": "langsmith_forums",
    "blog": "langsmith_blogs",
}
