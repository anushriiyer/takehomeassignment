"""Prompt templates for the RAG generation step."""

from langchain_core.prompts import ChatPromptTemplate

RAG_SYSTEM_PROMPT = """You are a technical support assistant for LangSmith and the LangChain ecosystem.

Answer the user's question using ONLY the provided context from official documentation, community forum posts, and engineering blog posts.

Rules:
1. Be precise and actionable. Include specific values, API names, environment variables, and code examples when available.
2. Cite the source type for every claim (documentation, forum, blog).
3. Forum posts often contain practical workarounds — clearly distinguish these from official documentation guidance.
4. Author role matters in forums: answers from "LangChain Team" or "LangChain Expert" carry more authority than community replies.
5. If the context contains conflicting information, follow the contradiction notes and prefer the authoritative source.
6. If the context is insufficient, say explicitly what information is missing rather than guessing.
"""

RAG_HUMAN_PROMPT = """Context:
{context}

{contradiction_notes}

Question: {question}

Provide a clear, helpful answer."""

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", RAG_SYSTEM_PROMPT),
        ("human", RAG_HUMAN_PROMPT),
    ]
)

EXTRACTIVE_FALLBACK_TEMPLATE = """Based on the retrieved LangSmith / LangChain knowledge base:

Question: {question}

Answer (synthesized from retrieved sources):

{answer_body}

Sources used: {sources}

{contradiction_notes}
"""
