from typing import List

from langchain_core.documents import Document

from store.vector_store import similarity_search


def retrieve(query: str, k: int = 6) -> List[Document]:
    """Return the top-k most relevant document chunks for a query."""
    return similarity_search(query, k=k)


def format_context(docs: List[Document]) -> str:
    """
    Build a context string from retrieved docs, citing repo and file.
    Each chunk is prefixed with its source so the LLM can cite it.
    """
    parts = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        source = f"[{i}] {meta.get('repo_name', 'unknown')} → {meta.get('file_path', 'unknown')}"
        parts.append(f"{source}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)
