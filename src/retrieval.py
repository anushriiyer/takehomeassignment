"""Multi-source retrieval with weighted fusion using LangChain retrievers."""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun

from src.config import RETRIEVAL_K_PER_SOURCE, SOURCE_WEIGHTS


@dataclass
class ScoredDocument:
    document: Document
    score: float
    source_type: str
    retrieval_method: str = "hybrid"


@dataclass
class RetrievalResult:
    query: str
    documents: list[ScoredDocument] = field(default_factory=list)
    source_counts: dict[str, int] = field(default_factory=dict)


class WeightedMultiSourceRetriever(BaseRetriever):
    """Retrieve from multiple sources, apply source weights, and merge results."""

    vector_stores: dict[str, Chroma]
    bm25_retrievers: dict[str, BM25Retriever]
    k_per_source: int = RETRIEVAL_K_PER_SOURCE
    source_weights: dict[str, float] | None = None

    class Config:
        arbitrary_types_allowed = True

    def _retrieve_from_source(
        self, query: str, source_type: str
    ) -> list[ScoredDocument]:
        weight = (self.source_weights or SOURCE_WEIGHTS).get(source_type, 1.0)
        scored: list[ScoredDocument] = []

        # Vector retrieval
        vector_store = self.vector_stores.get(source_type)
        if vector_store:
            vector_docs = vector_store.similarity_search_with_score(query, k=self.k_per_source)
            for doc, distance in vector_docs:
                # Chroma returns distance (lower is better); convert to similarity
                similarity = 1.0 / (1.0 + distance)
                scored.append(
                    ScoredDocument(
                        document=doc,
                        score=similarity * weight,
                        source_type=source_type,
                        retrieval_method="vector",
                    )
                )

        # BM25 retrieval
        bm25 = self.bm25_retrievers.get(source_type)
        if bm25:
            bm25.k = self.k_per_source
            bm25_docs = bm25.invoke(query)
            for rank, doc in enumerate(bm25_docs):
                bm25_score = (len(bm25_docs) - rank) / len(bm25_docs)
                scored.append(
                    ScoredDocument(
                        document=doc,
                        score=bm25_score * weight * 0.8,
                        source_type=source_type,
                        retrieval_method="bm25",
                    )
                )

        return scored

    def _deduplicate(self, scored_docs: list[ScoredDocument]) -> list[ScoredDocument]:
        seen: dict[str, ScoredDocument] = {}
        for sd in scored_docs:
            key = sd.document.page_content[:200]
            if key not in seen or sd.score > seen[key].score:
                seen[key] = sd
        return sorted(seen.values(), key=lambda x: x.score, reverse=True)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun | None = None
    ) -> list[Document]:
        all_scored: list[ScoredDocument] = []
        for source_type in self.vector_stores:
            all_scored.extend(self._retrieve_from_source(query, source_type))

        deduped = self._deduplicate(all_scored)
        return [sd.document for sd in deduped]

    def retrieve_with_scores(self, query: str) -> RetrievalResult:
        """Retrieve with full scoring metadata for analysis and logging."""
        all_scored: list[ScoredDocument] = []
        for source_type in self.vector_stores:
            all_scored.extend(self._retrieve_from_source(query, source_type))

        deduped = self._deduplicate(all_scored)
        source_counts: dict[str, int] = {}
        for sd in deduped:
            source_counts[sd.source_type] = source_counts.get(sd.source_type, 0) + 1

        return RetrievalResult(
            query=query,
            documents=deduped,
            source_counts=source_counts,
        )
