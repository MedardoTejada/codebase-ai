import json
from datetime import datetime, timezone
from typing import List, Optional

import chromadb
from langchain_core.documents import Document
from langchain_chroma import Chroma

from config import CHROMA_DIR, CHROMA_COLLECTION
from indexer.embedder import get_embeddings

# Metadata collection name (separate from vectors)
_META_COLLECTION = "repo_guide_meta"


def _chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_vector_store() -> Chroma:
    return Chroma(
        client=_chroma_client(),
        collection_name=CHROMA_COLLECTION,
        embedding_function=get_embeddings(),
    )


# ---------------------------------------------------------------------------
# Repo-level metadata (indexed_at, file_count, url)
# ---------------------------------------------------------------------------

def _meta_collection():
    client = _chroma_client()
    return client.get_or_create_collection(_META_COLLECTION)


def save_repo_meta(repo_name: str, repo_url: str, file_count: int) -> None:
    col = _meta_collection()
    now = datetime.now(timezone.utc).isoformat()
    payload = json.dumps({
        "repo_url": repo_url,
        "indexed_at": now,
        "file_count": file_count,
    })
    # upsert using repo_name as id
    col.upsert(
        ids=[repo_name],
        documents=[payload],
        metadatas=[{"repo_name": repo_name}],
    )


def list_repos() -> List[dict]:
    col = _meta_collection()
    results = col.get(include=["documents", "metadatas"])
    repos = []
    for doc in results["documents"]:
        try:
            repos.append(json.loads(doc))
        except json.JSONDecodeError:
            pass
    repos.sort(key=lambda r: r.get("indexed_at", ""))
    return repos


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def delete_repo_docs(repo_name: str) -> None:
    """Remove all previously indexed chunks for a repo."""
    store = get_vector_store()
    # Chroma supports filtering by metadata
    existing = store._collection.get(
        where={"repo_name": repo_name},
        include=["documents"],
    )
    ids = existing.get("ids", [])
    if ids:
        store._collection.delete(ids=ids)


def index_documents(docs: List[Document], batch_size: int = 5000) -> int:
    """Add documents to the vector store. Returns count added."""
    if not docs:
        return 0
    store = get_vector_store()
    for i in range(0, len(docs), batch_size):
        store.add_documents(docs[i:i + batch_size])
    return len(docs)


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def similarity_search(query: str, k: int = 6) -> List[Document]:
    store = get_vector_store()
    return store.similarity_search(query, k=k)
