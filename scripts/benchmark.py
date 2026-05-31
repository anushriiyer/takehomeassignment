#!/usr/bin/env python3
"""Performance analysis: retrieval vs reranking quality metrics.

Measures Precision@5 before and after cross-encoder reranking, plus per-stage
latency, across 12 labelled eval queries covering all three source types.

Expected source labels are set based on which source type contains the ground-truth
answer for that query. Precision@5 counts how many of the top-5 retrieved/reranked
chunks come from that expected source type.

This is a proxy metric (source-type precision rather than relevance judgements),
but it reliably measures whether reranking improves surfacing the right source
for each query type.
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import FINAL_CONTEXT_K  # noqa: E402
from src.ingestion import build_bm25_retrievers, load_vector_stores  # noqa: E402
from src.reranker import rerank_retrieval_result  # noqa: E402
from src.retrieval import WeightedMultiSourceRetriever  # noqa: E402

# (query, expected_primary_source_type)
# Chosen so each query has one clearly dominant source in the knowledge base.
EVAL_QUERIES = [
    # --- Documentation-primary queries ---
    ("How do I view traces in the Messages view vs Details view in LangSmith", "documentation"),
    ("What offline evaluation types does LangSmith support for pre-deployment testing", "documentation"),
    ("How do I stream token-by-token output from a LangGraph deployment", "documentation"),
    ("How do I set up automation rules in LangSmith", "documentation"),
    ("How do I view usage and billing in LangSmith", "documentation"),

    # --- Blog-primary queries ---
    ("Why should I use traces instead of logs to understand what my AI agent is doing", "blog"),
    ("How does the Command primitive work for multi-agent communication in LangGraph", "blog"),
    ("What are reusable evaluator templates and how do they work in LangSmith", "blog"),
    ("What is the difference between token streams and agent streams", "blog"),

    # --- Forum-primary queries ---
    ("What environment variables do I need for LangSmith tracing and is LANGSMITH_ENDPOINT required", "forum"),
    ("How do I delete specific runs or traces in LangSmith using the Python SDK", "forum"),
    ("RecursiveCharacterTextSplitter import error in newer LangChain versions", "forum"),
]


def source_counts(docs: list) -> dict:
    counts: dict = {}
    for d in docs:
        st = d.metadata.get("source_type", "unknown")
        counts[st] = counts.get(st, 0) + 1
    return counts


def precision_at_k(docs, expected_source: str, k: int = 5) -> float:
    if not docs:
        return 0.0
    top = docs[:k]
    hits = sum(1 for d in top if d.metadata.get("source_type") == expected_source)
    return hits / min(k, len(top))


def main() -> None:
    vector_stores = load_vector_stores()
    bm25 = build_bm25_retrievers()
    retriever = WeightedMultiSourceRetriever(
        vector_stores=vector_stores,
        bm25_retrievers=bm25,
    )

    retrieval_metrics = []
    rerank_metrics = []
    pre_source_counts = []
    post_source_counts = []
    latencies = {"retrieval": [], "rerank": []}

    for query, expected_source in EVAL_QUERIES:
        t0 = time.perf_counter()
        retrieval_result = retriever.retrieve_with_scores(query)
        t1 = time.perf_counter()
        rerank_result = rerank_retrieval_result(retrieval_result, top_n=FINAL_CONTEXT_K)
        t2 = time.perf_counter()

        pre_docs = [sd.document for sd in retrieval_result.documents]
        post_docs = rerank_result.documents

        pre_p = precision_at_k(pre_docs, expected_source)
        post_p = precision_at_k(post_docs, expected_source)

        retrieval_metrics.append(pre_p)
        rerank_metrics.append(post_p)
        pre_source_counts.append(source_counts(pre_docs[:5]))
        post_source_counts.append(source_counts(post_docs))
        latencies["retrieval"].append(t1 - t0)
        latencies["rerank"].append(t2 - t1)
        print(f"  [{expected_source:13s}] pre={pre_p:.2f} post={post_p:.2f}  {query[:60]}")

    report = {
        "eval_queries": len(EVAL_QUERIES),
        "precision_at_5": {
            "before_rerank_mean": round(sum(retrieval_metrics) / len(retrieval_metrics), 3),
            "after_rerank_mean": round(sum(rerank_metrics) / len(rerank_metrics), 3),
            "improvement": round(
                sum(rerank_metrics) / len(rerank_metrics)
                - sum(retrieval_metrics) / len(retrieval_metrics),
                3,
            ),
        },
        "latency_seconds": {
            "retrieval_mean": round(sum(latencies["retrieval"]) / len(latencies["retrieval"]), 3),
            "rerank_mean": round(sum(latencies["rerank"]) / len(latencies["rerank"]), 3),
            "total_mean": round(
                (sum(latencies["retrieval"]) + sum(latencies["rerank"])) / len(EVAL_QUERIES), 3
            ),
        },
        "per_query": [
            {
                "query": q,
                "expected_source": exp,
                "precision_pre_rerank": round(pre, 3),
                "precision_post_rerank": round(post, 3),
                "delta": round(post - pre, 3),
                "pre_rerank_source_counts": src_pre,
                "post_rerank_source_counts": src_post,
            }
            for (q, exp), pre, post, src_pre, src_post
            in zip(EVAL_QUERIES, retrieval_metrics, rerank_metrics, pre_source_counts, post_source_counts)
        ],
    }

    out_path = ROOT / "examples" / "performance_analysis.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("=== Performance Analysis ===")
    print(json.dumps(report["precision_at_5"], indent=2))
    print(json.dumps(report["latency_seconds"], indent=2))
    print(f"\nFull report: {out_path}")


if __name__ == "__main__":
    main()
