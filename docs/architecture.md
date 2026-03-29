# Architecture

## Overview

repo-guide is a RAG (Retrieval-Augmented Generation) agent that lets you index any GitHub repository and ask questions about it in natural language. The system clones the repo, splits the code into chunks, converts them into vector embeddings, stores them locally, and uses an LLM to answer questions based on retrieved context.

```
GitHub URL
    │
    ▼
┌─────────────┐
│   Cloner    │  GitPython — clones repo to disk (data/repos/)
└──────┬──────┘
       │
    ▼
┌─────────────┐
│   Parser    │  LangChain RecursiveCharacterTextSplitter
│             │  Reads supported files → splits into chunks (1000 chars, 200 overlap)
└──────┬──────┘
       │
    ▼
┌─────────────┐
│  Embedder   │  HuggingFace all-MiniLM-L6-v2 (runs locally on CPU)
│             │  Converts each chunk into a 384-dimension vector
└──────┬──────┘
       │
    ▼
┌─────────────┐
│  ChromaDB   │  Persistent local vector store (data/chroma/)
│             │  Stores vectors + metadata (repo, file path, extension)
└──────┬──────┘
       │
    ▼  (at query time)
┌─────────────┐
│  Retriever  │  Similarity search — returns top-6 most relevant chunks
└──────┬──────┘
       │
    ▼
┌─────────────┐
│  LLM Chain  │  LangChain + Ollama (llama3.2 by default, runs locally)
│             │  Prompt includes context + source citations
└─────────────┘
```

---

## Components

### `indexer/cloner.py`
Clones a GitHub repo using GitPython. Supports private repos via `GITHUB_TOKEN` injected into the HTTPS URL. Has a 30-second timeout using UNIX signals. If the repo was already cloned, it deletes and re-clones (full reindex).

### `indexer/parser.py`
Walks the cloned directory recursively. Skips hidden directories (`.git`, `.github`), `node_modules`, and unsupported file types. Splits each file with `RecursiveCharacterTextSplitter` (chunk size: 1000, overlap: 200). Each chunk carries metadata: `repo_url`, `repo_name`, `file_path`, `extension`.

### `indexer/embedder.py`
Loads `sentence-transformers/all-MiniLM-L6-v2` from HuggingFace and runs it on CPU. The model is cached after the first load. Embeddings are normalized (unit vectors), which improves cosine similarity quality.

### `store/vector_store.py`
Wraps ChromaDB via `langchain_chroma`. Documents are upserted in batches of 5000 (ChromaDB max batch: 5461). Also maintains a separate `repo_guide_meta` collection with per-repo metadata (URL, indexed_at timestamp, file count).

### `agent/retriever.py`
Runs a similarity search against ChromaDB and formats the top-6 results into a numbered context string with `[repo_name → file_path]` citations.

### `agent/chain.py`
Builds a LangChain LCEL chain: context + question → PromptTemplate → OllamaLLM → StrOutputParser. The prompt instructs the LLM to answer only from the provided context and always cite sources.

---

## Tools & libraries

| Component | Tool | Why |
|---|---|---|
| Orchestration | LangChain (LCEL) | Chain composition, splitters, document model |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` | Free, runs locally, fast on CPU, good quality for code |
| Vector store | ChromaDB | Local persistence, no server needed, easy metadata filtering |
| LLM | Ollama (llama3.2) | Runs fully locally, no API cost, easy model swapping |
| Repo cloning | GitPython | Pure Python, supports token injection for private repos |
| Config | python-dotenv | Simple `.env` override pattern |

---

## Potential improvements

### LLM
The current setup uses `llama3.2` via Ollama, which runs locally on CPU/GPU. This works well for experimentation but has limitations:

- **Better local models**: `llama3.1:8b`, `mistral`, `codellama` (specialized for code), `deepseek-coder` are stronger alternatives for code understanding.
- **Cloud LLMs**: Replace Ollama with `langchain_openai` (GPT-4o) or `langchain_anthropic` (Claude) for significantly better reasoning and longer context windows. Only requires changing `agent/chain.py` and adding an API key.
- **Larger context**: Current LLMs have limited context windows. Switching to models with 128k+ context (GPT-4o, Claude 3.5) would allow passing more retrieved chunks.

### Embeddings
- `all-MiniLM-L6-v2` is fast and lightweight but was not trained specifically on code.
- **Better alternative**: `microsoft/codebert-base` or `nomic-ai/nomic-embed-text-v1.5` produce higher-quality embeddings for source code and would improve retrieval relevance.
- **OpenAI embeddings**: `text-embedding-3-small` outperforms local models in most benchmarks at low cost.

### Retrieval
- Currently does flat similarity search (top-6 chunks). For large repos this can miss context.
- **Improvements**: hybrid search (BM25 + vector), reranking with a cross-encoder model, or increasing `k` and filtering by file type.
- **Multi-repo search**: Currently searches across all indexed repos. Adding a `--repo` filter flag would improve precision.

### Indexing
- No incremental indexing: every `index` call does a full re-clone and re-embed.
- **Improvement**: track file hashes and only re-embed changed files.
- The 30-second clone timeout is too short for large repos (TheAlgorithms/Python took several minutes). This should be configurable or removed for large repos.

### Interface
- Currently CLI only. A simple web UI (FastAPI + minimal frontend) or a chat interface (Gradio, Streamlit) would make it more accessible.
