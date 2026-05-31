"""Ingest documents into per-source Chroma vector stores via LangChain."""

from __future__ import annotations

from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from src.chunkers import load_all_chunks
from src.config import CHROMA_DIR, COLLECTION_NAMES, EMBEDDING_MODEL


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_vector_stores(
    chunks_by_source: dict[str, list[Document]] | None = None,
    persist: bool = True,
) -> dict[str, Chroma]:
    """Create or rebuild Chroma collections for each source type."""
    chunks_by_source = chunks_by_source or load_all_chunks()
    embeddings = get_embeddings()
    stores: dict[str, Chroma] = {}

    if persist and CHROMA_DIR.exists():
        import shutil

        shutil.rmtree(CHROMA_DIR)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    for source_type, docs in chunks_by_source.items():
        if not docs:
            continue
        stores[source_type] = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name=COLLECTION_NAMES[source_type],
            persist_directory=str(CHROMA_DIR),
        )
    return stores


def build_bm25_retrievers(
    chunks_by_source: dict[str, list[Document]] | None = None,
) -> dict[str, BM25Retriever]:
    """Build BM25 retrievers for hybrid search per source."""
    chunks_by_source = chunks_by_source or load_all_chunks()
    retrievers: dict[str, BM25Retriever] = {}

    for source_type, docs in chunks_by_source.items():
        if not docs:
            continue
        retriever = BM25Retriever.from_documents(docs)
        retriever.k = 8
        retrievers[source_type] = retriever
    return retrievers


def load_vector_stores() -> dict[str, Chroma]:
    """Load existing persisted Chroma collections."""
    embeddings = get_embeddings()
    stores: dict[str, Chroma] = {}

    for source_type, collection_name in COLLECTION_NAMES.items():
        stores[source_type] = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DIR),
        )
    return stores
