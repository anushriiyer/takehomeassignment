#!/usr/bin/env python3
"""Run the 15 example queries and save results to examples/example_results.json."""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import RAGPipeline  # noqa: E402

EXAMPLE_QUERIES = [
    "How do I enable LangSmith tracing for my LangChain or Python project?",
    "How do I delete traces or runs in LangSmith, and how quickly are they removed?",
    "What evaluation types does LangSmith offer and how do I choose between them?",
    "How do I stream agent responses token by token using the LangGraph SDK?",
    "How do I build a multi-agent system where agents communicate in LangGraph?",
    "Why are traces more important than logs for debugging AI agents?",
    "How do I run and analyze an experiment comparing two prompt versions in LangSmith?",
    "How do I set up webhooks and automation rules in LangSmith?",
    "How do I track LLM costs and manage billing in LangSmith?",
    "What environment variables do I need to set up LangSmith tracing, and is LANGSMITH_ENDPOINT required?",
    "How do I evaluate whether my agent took the correct steps using trajectory evaluation?",
    "How do I control or prevent unwanted tool calls in my LangChain agent?",
    "What are best practices for running LLM-based tests at scale without hitting rate limits?",
    "How do I make sense of 100,000 traces a day and understand agent behavior at scale?",
    "I'm getting an import error for RecursiveCharacterTextSplitter — how do I fix it in newer LangChain versions?",
]


def main() -> None:
    out_dir = ROOT / "examples"
    out_dir.mkdir(exist_ok=True)
    results_path = out_dir / "example_results.json"

    pipeline = RAGPipeline()
    results = []

    print(f"Running {len(EXAMPLE_QUERIES)} example queries...\n")

    for i, question in enumerate(EXAMPLE_QUERIES, 1):
        print(f"[{i}/{len(EXAMPLE_QUERIES)}] {question}")
        start = time.perf_counter()
        response = pipeline.query(question, save_log=True)
        elapsed = time.perf_counter() - start

        results.append(
            {
                "question": question,
                "answer": response.answer,
                "sources_used": response.sources_used,
                "source_counts": response.source_counts,
                "retrieval_count": response.retrieval_count,
                "rerank_count": response.rerank_count,
                "contradictions": response.contradictions,
                "latency_seconds": round(elapsed, 2),
                "log_path": response.log_path,
            }
        )
        print(f"  → {response.source_counts} ({elapsed:.1f}s)\n")

    results_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    main()
