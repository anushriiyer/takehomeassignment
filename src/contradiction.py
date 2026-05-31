"""Detect and resolve contradictions between knowledge sources.

Real contradictions in this LangSmith / LangChain corpus:
  1. Bulk delete API: forum user says absent, LangChain Team says batch endpoint exists
  2. Trace deletion timing: forum says weekend/non-peak, docs say within a few hours
  3. LANGSMITH_ENDPOINT: forum user includes it, expert says not needed for hosted service
  4. Tracing setup: some examples show @traceable, expert clarifies LangChain auto-traces

Resolution authority: documentation > blog > forum
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from langchain_core.documents import Document

from src.config import SOURCE_AUTHORITY

# Numeric claims: rate limits, timeouts, retention periods, etc.
NUMERIC_PATTERN = re.compile(
    r"(\d[\d,]*)\s*"
    r"(requests?\s*(?:per\s*)?(?:min(?:ute)?|sec(?:ond)?)|req/min"
    r"|tokens?|days?\s*retention|hours?|KB|MB|GB"
    r"|traces?\s*per\s*request|runs?\s*per\s*request)",
    re.IGNORECASE,
)

# Boolean / presence claims — (regex, canonical key)
# Patterns tuned to match actual forum text in this corpus.
BOOLEAN_CLAIMS: list[tuple[re.Pattern[str], str]] = [
    # "doesn't have a direct bulk delete API" (forum_199 early post)
    (re.compile(r"doesn?'t have\s+(?:a\s+)?(?:direct\s+)?bulk\s+delete|no\s+(?:direct\s+)?bulk\s+delete\s+api", re.I), "bulk_delete_api_absent"),
    # "There is a batch delete endpoint" (forum_199 LangChain Team post)
    (re.compile(r"batch\s+delete\s+endpoint", re.I), "bulk_delete_api_present"),
    # "We process these deletions over the weekend now" (forum_199)
    (re.compile(r"(?:process|deletion|delete).*\bweekend\b|\bweekend\b.*(?:process|deletion)", re.I), "trace_deletion_weekend"),
    # "usually within a few hours" (forum_199 / docs)
    (re.compile(r"within\s+a?\s*few\s+hours?|usually\s+within.*hours?", re.I), "trace_deletion_hours"),
    # "LANGSMITH_ENDPOINT=https://..." — user includes it in .env (forum_3077 Q post)
    (re.compile(r"LANGSMITH_ENDPOINT\s*=\s*https?://", re.I), "langsmith_endpoint_set"),
    # Expert clarifies it is not needed for the hosted service (forum_3077 expert post)
    (re.compile(
        r"LANGSMITH_ENDPOINT\s+is\s+only\s+needed"
        r"|not\s+sure\s+you\s+need\s+LANGSMITH_ENDPOINT"
        r"|(?:don'?t|do\s+not)\s+need\s+LANGSMITH_ENDPOINT"
        r"|can\s+omit\s+(?:it\s+entirely|LANGSMITH_ENDPOINT)",
        re.I,
    ), "langsmith_endpoint_optional"),
    # "LangChain auto-traces all invocations" (forum_3077 expert post)
    (re.compile(r"LangChain\s+auto.?trac", re.I), "langchain_autotraces"),
    (re.compile(r"tracing.*not\s+OpenAI.specific|not\s+OpenAI.specific.*tracing", re.I), "tracing_provider_agnostic"),
]

# Map each boolean key to its logical opposite for cross-source conflict detection
BOOLEAN_OPPOSITES: dict[str, str] = {
    "bulk_delete_api_absent": "bulk_delete_api_present",
    "bulk_delete_api_present": "bulk_delete_api_absent",
    "trace_deletion_weekend": "trace_deletion_hours",
    "trace_deletion_hours": "trace_deletion_weekend",
    "langsmith_endpoint_set": "langsmith_endpoint_optional",
    "langsmith_endpoint_optional": "langsmith_endpoint_set",
}

RATE_LIMIT_CLAIMS = re.compile(
    r"(\d[\d,]*)\s*(?:requests?\s*(?:per\s*)?min|req/min)",
    re.IGNORECASE,
)


@dataclass
class Contradiction:
    topic: str
    claims: list[dict[str, str]]
    resolution: str
    authoritative_source: str


@dataclass
class ContradictionReport:
    contradictions: list[Contradiction] = field(default_factory=list)
    has_contradictions: bool = False
    resolution_notes: list[str] = field(default_factory=list)


def _source_label(doc: Document) -> str:
    st = doc.metadata.get("source_type", "unknown")
    title = (
        doc.metadata.get("title")
        or doc.metadata.get("thread_title")
        or doc.metadata.get("source_file", "unknown")
    )
    return f"{st}:{title}"


def _extract_numeric_claims(text: str) -> dict[str, str]:
    claims: dict[str, str] = {}
    for match in NUMERIC_PATTERN.finditer(text):
        unit_key = re.sub(r"\s+", "_", match.group(2).lower().strip())
        claims[f"numeric_{unit_key}"] = match.group(0)
    return claims


def _extract_boolean_claims(text: str) -> dict[str, str]:
    claims: dict[str, str] = {}
    for pattern, key in BOOLEAN_CLAIMS:
        if pattern.search(text):
            claims[key] = "true"
    return claims


def _add_contradiction(
    report: ContradictionReport,
    topic: str,
    claims: list[dict[str, str]],
) -> None:
    authoritative = None
    for authority_source in SOURCE_AUTHORITY:
        matching = [c for c in claims if c["source"] == authority_source]
        if matching:
            authoritative = matching[0]
            break
    if authoritative is None:
        authoritative = claims[0]

    resolution = (
        f"Conflicting information detected for '{topic}'. "
        f"Deferring to {authoritative['label']} as the authoritative source "
        f"(value: {authoritative['value']})."
    )
    report.contradictions.append(
        Contradiction(
            topic=topic,
            claims=[{"source": c["label"], "value": c["value"]} for c in claims],
            resolution=resolution,
            authoritative_source=authoritative["source"],
        )
    )
    report.resolution_notes.append(resolution)


def detect_contradictions(documents: list[Document]) -> ContradictionReport:
    """Find conflicting claims across retrieved documents.

    Boolean contradictions: fire when opposing keys appear in at least two
    *different documents* (different labels), regardless of source type.
    Forum threads often contain contradictory posts — this catches those too.

    Numeric contradictions: require different source *types* to avoid false
    positives from tables that list multiple values for different tiers.
    """
    report = ContradictionReport()
    topic_claims: dict[str, list[dict[str, str]]] = {}

    for doc in documents:
        text = doc.page_content
        source = doc.metadata.get("source_type", "unknown")
        label = _source_label(doc)

        for key, value in {**_extract_numeric_claims(text), **_extract_boolean_claims(text)}.items():
            topic_claims.setdefault(key, []).append(
                {"source": source, "label": label, "value": value, "text": text[:300]}
            )

    # Boolean opposite pairs — require claims from at least 2 different chunks
    # We use text[:80] as a unique-per-chunk proxy since all posts in a thread
    # share the same thread_title label.
    flagged_pairs: set[frozenset[str]] = set()
    for topic, claims in topic_claims.items():
        opposite = BOOLEAN_OPPOSITES.get(topic)
        if opposite and opposite in topic_claims:
            pair_key = frozenset({topic, opposite})
            if pair_key in flagged_pairs:
                continue
            flagged_pairs.add(pair_key)
            combined = claims + topic_claims[opposite]
            if len({c["text"][:80] for c in combined}) > 1:  # at least 2 distinct chunks
                _add_contradiction(report, f"{topic} vs {opposite}", combined)

    # Numeric contradictions: same unit, different values, different source types
    for topic, claims in topic_claims.items():
        if not topic.startswith("numeric_"):
            continue
        if len({c["value"] for c in claims}) > 1 and len({c["source"] for c in claims}) > 1:
            _add_contradiction(report, topic, claims)

    report.has_contradictions = len(report.contradictions) > 0
    return report


def format_contradiction_disclaimer(report: ContradictionReport) -> str:
    if not report.has_contradictions:
        return ""

    lines = ["\n\n**Note on conflicting sources:**"]
    for c in report.contradictions:
        sources = ", ".join(f"{cl['source']} ({cl['value']})" for cl in c.claims)
        lines.append(f"- {c.topic}: {sources}. {c.resolution}")
    return "\n".join(lines)
