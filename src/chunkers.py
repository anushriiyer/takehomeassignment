"""Chunking strategies for the three source types.

Docs: split by markdown headers so each chunk maps to one section.
Forums: split per post (not per thread) to keep author/role signals intact.
Blogs: paragraph-level split with overlap to avoid cutting mid-argument.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from src.config import BLOGS_DIR, DOCUMENTATION_DIR, FORUMS_DIR

DOC_HEADERS = [
    ("#", "section"),
    ("##", "subsection"),
    ("###", "subsubsection"),
]

BLOG_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""],
)

FORUM_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def _strip_doc_index_header(text: str) -> str:
    """Strip the navigation blockquote added to each scraped LangSmith doc.

    Each file starts with:
        > ## Documentation Index
        > Fetch the complete documentation index at: ...
    That's site chrome, not content.
    """
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        stripped = lines[i].lstrip()
        if stripped.startswith("> ") or stripped in (">\n", ">\r\n"):
            i += 1
        elif stripped.strip() == "" and i > 0:
            i += 1
            break
        else:
            break
    return "".join(lines[i:])


def _strip_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, match.group(2)


def chunk_documentation(path: Path) -> list[Document]:
    """Split docs by markdown headers to preserve section hierarchy."""
    text = path.read_text(encoding="utf-8")
    text = _strip_doc_index_header(text)
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=DOC_HEADERS)
    header_chunks = header_splitter.split_text(text)

    # Further split oversized sections while keeping metadata
    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    documents: list[Document] = []
    for chunk in header_chunks:
        sub_chunks = size_splitter.split_documents([chunk]) if len(chunk.page_content) > 700 else [chunk]
        for sub in sub_chunks:
            sub.metadata.update(
                {
                    "source_type": "documentation",
                    "source_file": path.name,
                    "title": path.stem.replace("-", " ").title(),
                }
            )
            documents.append(sub)
    return documents


def chunk_forum(path: Path) -> list[Document]:
    """One chunk per post (not per thread). Author role is embedded in the text
    so the reranker can distinguish LangChain Team answers from community replies.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    documents: list[Document] = []

    tags = data.get("tags") or []
    url = data.get("url", "")

    for i, post in enumerate(data["posts"]):
        role = post.get("role", "user")
        role_label = f" [{role}]" if role and role != "user" else ""
        content = (
            f"Forum thread: {data['title']}\n"
            f"Tags: {', '.join(tags)}\n"
            f"Author: {post['author']}{role_label}\n\n"
            f"{post['body']}"
        )
        base_meta = {
            "source_type": "forum",
            "source_file": path.name,
            "thread_id": data["id"],
            "thread_title": data["title"],
            "author": post["author"],
            "author_role": role,
            "post_index": i,
            "post_number": post.get("post_number", i + 1),
            "date": data.get("date", ""),
            "url": url,
            "tags": ", ".join(tags),
        }
        post_docs = FORUM_SPLITTER.create_documents([content], metadatas=[base_meta])
        documents.extend(post_docs)

    return documents


def chunk_blog(path: Path) -> list[Document]:
    """Split blogs by paragraph with overlap for narrative continuity."""
    raw = path.read_text(encoding="utf-8")
    meta, body = _strip_front_matter(raw)
    base_meta = {
        "source_type": "blog",
        "source_file": path.name,
        "title": meta.get("title", path.stem.replace("-", " ").title()),
        "author": meta.get("author", "Unknown"),
        "date": meta.get("date", ""),
    }
    return BLOG_SPLITTER.create_documents([body], metadatas=[base_meta])


def load_all_chunks() -> dict[str, list[Document]]:
    """Load and chunk all knowledge sources."""
    chunks: dict[str, list[Document]] = {
        "documentation": [],
        "forum": [],
        "blog": [],
    }

    for path in sorted(DOCUMENTATION_DIR.glob("*.md")):
        chunks["documentation"].extend(chunk_documentation(path))

    for path in sorted(FORUMS_DIR.glob("*.json")):
        chunks["forum"].extend(chunk_forum(path))

    for path in sorted(BLOGS_DIR.glob("*.md")):
        chunks["blog"].extend(chunk_blog(path))

    return chunks
