#!/usr/bin/env python3
"""Run a single query against the LangSmith / LangChain RAG pipeline."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rich.console import Console  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.table import Table  # noqa: E402

from src.pipeline import RAGPipeline  # noqa: E402

console = Console()


def main() -> None:
    if len(sys.argv) < 2:
        console.print("[red]Usage:[/red] python scripts/query.py \"your question here\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    pipeline = RAGPipeline()
    response = pipeline.query(question)

    console.print(Panel(response.answer, title="Answer", border_style="green"))

    table = Table(title="Sources Used")
    table.add_column("Type")
    table.add_column("Title")
    table.add_column("File")
    for src in response.sources_used:
        table.add_row(
            str(src.get("source_type")),
            str(src.get("title") or "-"),
            str(src.get("file") or "-"),
        )
    console.print(table)

    console.print(f"\nRetrieved: {response.retrieval_count} | Reranked to: {response.rerank_count}")
    console.print(f"Source breakdown: {response.source_counts}")
    if response.contradictions:
        console.print(f"[yellow]Contradictions detected: {len(response.contradictions)}[/yellow]")
    if response.log_path:
        console.print(f"Log saved: {response.log_path}")


if __name__ == "__main__":
    main()
