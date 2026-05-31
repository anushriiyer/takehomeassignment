"""Structured logging for RAG query tracing."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import LOGS_DIR

LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("nexusflow.rag")
logger.setLevel(logging.INFO)

if not logger.handlers:
    console = logging.StreamHandler()
    console.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(console)

    file_handler = logging.FileHandler(LOGS_DIR / "rag_queries.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(file_handler)


def log_query_event(event_type: str, payload: dict[str, Any]) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        **payload,
    }
    logger.info(json.dumps(entry, default=str))


def save_query_record(record: dict[str, Any], filename: str | None = None) -> Path:
    """Persist full query record as JSON for analysis."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = LOGS_DIR / (filename or f"query_{ts}.json")
    path.write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
    return path
