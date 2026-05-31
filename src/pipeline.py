"""End-to-end LangChain RAG pipeline for LangSmith / LangChain technical support."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.config import CHROMA_DIR, FINAL_CONTEXT_K, GEMINI_MODEL, GOOGLE_API_KEY, OPENAI_API_KEY, OPENAI_MODEL
from src.contradiction import detect_contradictions, format_contradiction_disclaimer
from src.ingestion import build_bm25_retrievers, get_embeddings, load_vector_stores
from src.logging_utils import log_query_event, save_query_record
from src.prompts import EXTRACTIVE_FALLBACK_TEMPLATE, RAG_PROMPT
from src.reranker import rerank_retrieval_result
from src.retrieval import WeightedMultiSourceRetriever


@dataclass
class RAGResponse:
    question: str
    answer: str
    sources_used: list[dict[str, Any]] = field(default_factory=list)
    source_counts: dict[str, int] = field(default_factory=dict)
    retrieval_count: int = 0
    rerank_count: int = 0
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    log_path: str = ""


class RAGPipeline:
    """Multi-source RAG pipeline with retrieval, reranking, and contradiction handling."""

    def __init__(
        self,
        vector_stores: dict[str, Chroma] | None = None,
        bm25_retrievers: dict[str, BM25Retriever] | None = None,
    ) -> None:
        if vector_stores is None:
            if not CHROMA_DIR.exists():
                raise FileNotFoundError(
                    "Vector store not found. Run `python scripts/ingest.py` first."
                )
            vector_stores = load_vector_stores()

        self.vector_stores = vector_stores
        self.bm25_retrievers = bm25_retrievers or build_bm25_retrievers()
        self.retriever = WeightedMultiSourceRetriever(
            vector_stores=self.vector_stores,
            bm25_retrievers=self.bm25_retrievers,
        )
        self.llm = self._build_llm()

    def _build_llm(self):
        if GOOGLE_API_KEY:
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=GOOGLE_API_KEY,
                temperature=0,
            )
        if OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=OPENAI_MODEL, temperature=0)
        return None

    def _format_context(self, documents: list[Document]) -> str:
        parts: list[str] = []
        for i, doc in enumerate(documents, 1):
            meta = doc.metadata
            source_type = meta.get("source_type", "unknown")
            title = (
                meta.get("title")
                or meta.get("thread_title")
                or meta.get("source_file", "")
            )
            parts.append(
                f"[{i}] ({source_type}) {title}\n{doc.page_content}"
            )
        return "\n\n---\n\n".join(parts)

    def _format_sources(self, documents: list[Document]) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []
        for doc in documents:
            meta = doc.metadata
            sources.append(
                {
                    "source_type": meta.get("source_type"),
                    "title": meta.get("title") or meta.get("thread_title"),
                    "file": meta.get("source_file"),
                    "author": meta.get("author"),
                    "date": meta.get("date"),
                    "preview": doc.page_content[:200],
                }
            )
        return sources

    def _generate_extractive_answer(
        self, question: str, documents: list[Document]
    ) -> str:
        """Fallback when no LLM API key is configured."""
        if not documents:
            return "I couldn't find relevant information in the knowledge base for this question."

        snippets: list[str] = []
        for doc in documents[:3]:
            meta = doc.metadata
            st = meta.get("source_type", "source")
            title = meta.get("title") or meta.get("thread_title") or meta.get("source_file")
            snippets.append(f"From {st} ({title}):\n{doc.page_content[:500]}")

        source_summary = ", ".join(
            sorted({d.metadata.get("source_type", "?") for d in documents})
        )
        return EXTRACTIVE_FALLBACK_TEMPLATE.format(
            question=question,
            answer_body="\n\n".join(snippets),
            sources=source_summary,
            contradiction_notes="",
        ).strip()

    def query(self, question: str, save_log: bool = True) -> RAGResponse:
        log_query_event("query_start", {"question": question})

        # Step 1: Multi-source weighted retrieval
        retrieval_result = self.retriever.retrieve_with_scores(question)
        log_query_event(
            "retrieval_complete",
            {
                "question": question,
                "pre_rerank_count": len(retrieval_result.documents),
                "source_counts": retrieval_result.source_counts,
            },
        )

        # Step 2: Cross-encoder reranking
        rerank_result = rerank_retrieval_result(
            retrieval_result, top_n=FINAL_CONTEXT_K
        )
        log_query_event(
            "rerank_complete",
            {
                "question": question,
                "pre_rerank_count": rerank_result.pre_rerank_count,
                "post_rerank_count": rerank_result.post_rerank_count,
                "source_counts": rerank_result.source_counts,
            },
        )

        # Step 3: Contradiction detection
        contradiction_report = detect_contradictions(rerank_result.documents)
        contradiction_notes = format_contradiction_disclaimer(contradiction_report)
        if contradiction_report.has_contradictions:
            log_query_event(
                "contradictions_detected",
                {
                    "question": question,
                    "count": len(contradiction_report.contradictions),
                    "topics": [c.topic for c in contradiction_report.contradictions],
                },
            )

        # Step 4: Generation
        context = self._format_context(rerank_result.documents)
        if self.llm:
            chain = (
                {
                    "context": lambda _: context,
                    "question": RunnablePassthrough(),
                    "contradiction_notes": lambda _: contradiction_notes,
                }
                | RAG_PROMPT
                | self.llm
                | StrOutputParser()
            )
            answer = chain.invoke(question)
            if contradiction_notes and contradiction_notes not in answer:
                answer += contradiction_notes
        else:
            answer = self._generate_extractive_answer(question, rerank_result.documents)
            if contradiction_notes:
                answer += contradiction_notes

        sources_used = self._format_sources(rerank_result.documents)

        log_query_event(
            "query_complete",
            {
                "question": question,
                "sources_used": [s["source_type"] for s in sources_used],
                "source_counts": rerank_result.source_counts,
            },
        )

        record = {
            "question": question,
            "answer": answer,
            "sources_used": sources_used,
            "source_counts": rerank_result.source_counts,
            "retrieval_count": len(retrieval_result.documents),
            "rerank_count": rerank_result.post_rerank_count,
            "contradictions": [
                {
                    "topic": c.topic,
                    "claims": c.claims,
                    "resolution": c.resolution,
                }
                for c in contradiction_report.contradictions
            ],
        }

        log_path = ""
        if save_log:
            path = save_query_record(record)
            log_path = str(path)

        return RAGResponse(
            question=question,
            answer=answer,
            sources_used=sources_used,
            source_counts=rerank_result.source_counts,
            retrieval_count=len(retrieval_result.documents),
            rerank_count=rerank_result.post_rerank_count,
            contradictions=record["contradictions"],
            log_path=log_path,
        )
