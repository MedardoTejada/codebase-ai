# repo-guide

RAG agent for codebase onboarding. Clone and index any GitHub repo, then ask questions in natural language. Answers cite the source file and repo.

## Stack

- **LangChain** — orchestration
- **ChromaDB** — local vector store (persistent)
- **HuggingFace** `all-MiniLM-L6-v2` — embeddings (runs locally, no API key needed)
- **Ollama** — local LLM inference
- **GitPython** — repo cloning

## Prerequisites

1. **Python 3.10+**
2. **Ollama** running locally with a model pulled:
   ```bash
   ollama pull llama3.2
   ollama serve
   ```

## Setup

```bash
git clone <this-repo>
cd repo-guide

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env if needed (GITHUB_TOKEN for private repos, custom OLLAMA_MODEL)
```

## Usage

### Index a repo

```bash
python main.py index https://github.com/owner/repo
```

- Clones the repo (30 s timeout)
- Parses all supported files and splits into chunks
- Embeds with `all-MiniLM-L6-v2` and stores in ChromaDB
- Re-indexing the same URL replaces all previous chunks (keeps it fresh)

### Ask a question

```bash
python main.py ask "How is authentication handled?"
python main.py ask "Where are database migrations defined?"
python main.py ask "What does the UserService class do?"
```

Responses cite `[repo_name → file_path]` for every claim.

### List indexed repos

```bash
python main.py list
```

Shows URL, file count, and timestamp for each indexed repo.

## Supported file types

| Category | Extensions |
|----------|-----------|
| Code | `.py` `.java` `.js` `.ts` `.kt` `.feature` `.karate` |
| Docs | `.md` `.txt` `.yaml` `.yml` `.json` |

## Private repos

Add your GitHub personal access token to `.env`:

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

The token is injected into the HTTPS clone URL automatically.

## Configuration

All settings live in `config.py` and can be overridden via `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_TOKEN` | *(empty)* | PAT for private repos |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama3.2` | Model to use for answers |

## Project structure

```
repo-guide/
├── config.py            # All configuration
├── main.py              # CLI entry point
├── indexer/
│   ├── cloner.py        # Git clone with timeout
│   ├── parser.py        # File traversal + chunking
│   └── embedder.py      # HuggingFace embeddings (cached)
├── store/
│   └── vector_store.py  # ChromaDB read/write operations
├── agent/
│   ├── retriever.py     # Similarity search + context formatting
│   └── chain.py         # LangChain RAG chain (Ollama)
├── data/
│   ├── repos/           # Cloned repos (git-ignored)
│   └── chroma/          # Persistent vector DB (git-ignored)
├── .env.example
├── .gitignore
└── requirements.txt
```
