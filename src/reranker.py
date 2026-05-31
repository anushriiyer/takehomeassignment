"""Cross-encoder reranking: top-N candidates from weighted retrieval → top-5."""

from __future__ import annotations

from dataclasses import dataclass

from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.documents import Document

from src.config import FINAL_CONTEXT_K, RERANKER_MODEL, RERANK_TOP_N
from src.retrieval import RetrievalResult


@dataclass
class RerankResult:
    query: str
    documents: list[Document]
    pre_rerank_count: int
    post_rerank_count: int
    source_counts: dict[str, int]


def build_reranker(top_n: int = RERANK_TOP_N) -> CrossEncoderReranker:
    model = HuggingFaceCrossEncoder(model_name=RERANKER_MODEL)
    return CrossEncoderReranker(model=model, top_n=top_n)


def rerank_retrieval_result(
    retrieval_result: RetrievalResult,
    top_n: int = FINAL_CONTEXT_K,
) -> RerankResult:
    """Rerank pre-fetched documents using cross-encoder scoring."""
    if not retrieval_result.documents:
        return RerankResult(
            query=retrieval_result.query,
            documents=[],
            pre_rerank_count=0,
            post_rerank_count=0,
            source_counts={},
        )

    query = retrieval_result.query
    docs = [sd.document for sd in retrieval_result.documents]
    pre_count = len(docs)

    reranker = build_reranker(top_n=min(top_n, len(docs)))
    reranked = reranker.compress_documents(docs, query)

    source_counts: dict[str, int] = {}
    for doc in reranked:
        st = doc.metadata.get("source_type", "unknown")
        source_counts[st] = source_counts.get(st, 0) + 1

    return RerankResult(
        query=query,
        documents=reranked[:top_n],
        pre_rerank_count=pre_count,
        post_rerank_count=len(reranked[:top_n]),
        source_counts=source_counts,
    )


