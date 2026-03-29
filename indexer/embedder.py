from langchain_huggingface import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL

_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a cached HuggingFace embeddings instance."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings
