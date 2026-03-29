from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import SUPPORTED_EXTENSIONS, CHUNK_SIZE, CHUNK_OVERLAP


def parse_repo(repo_path: Path, repo_url: str) -> List[Document]:
    """
    Walk the repo directory, read supported files, split into chunks.
    Each Document carries metadata: repo_url, repo_name, file_path, extension.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )

    docs: List[Document] = []
    repo_name = repo_path.name

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        # Skip hidden directories (.git, .github, node_modules …)
        if any(part.startswith(".") for part in file_path.parts):
            continue
        if "node_modules" in file_path.parts:
            continue

        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if not text.strip():
            continue

        relative = file_path.relative_to(repo_path)
        metadata = {
            "repo_url": repo_url,
            "repo_name": repo_name,
            "file_path": str(relative),
            "extension": file_path.suffix.lower(),
        }

        chunks = splitter.create_documents([text], metadatas=[metadata])
        docs.extend(chunks)

    return docs
