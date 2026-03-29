# repo-guide

RAG agent for codebase onboarding. Clone and index any GitHub repository, then ask questions about it in natural language. Answers cite the source file and repo.

## How it works

1. You give it a GitHub URL
2. It clones the repo, splits the code into chunks, and generates vector embeddings
3. When you ask a question, it finds the most relevant chunks and sends them to a local LLM
4. The LLM answers based only on the actual code, always citing the source file

Everything runs locally — no cloud APIs required.

## Quick start

**Prerequisites:** Python 3.10+, [Ollama](https://ollama.com) installed and running.

Full setup instructions → [docs/installation.md](docs/installation.md)

```bash
# 1. Clone and install
git clone https://github.com/MedardoTejada/codebase-ai.git
cd codebase-ai
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env and add your HF_TOKEN (see docs/installation.md)

# 3. Download the LLM (one-time, ~2 GB)
ollama pull llama3.2

# 4. Index a repo
python main.py index https://github.com/owner/repo

# 5. Ask questions
python main.py ask "what does this project do?"
python main.py ask "how is authentication handled?"
python main.py ask "where are database connections configured?"
```

## Commands

```
python main.py index <github_url>    Clone and index a repository
python main.py ask "<question>"      Ask a question about indexed repos
python main.py list                  Show all indexed repositories
```

## Configuration

All settings live in `config.py` and can be overridden via `.env`:

| Variable | Default | Description |
|---|---|---|
| `HF_TOKEN` | *(empty)* | HuggingFace access token (avoids rate limits on model downloads) |
| `GITHUB_TOKEN` | *(empty)* | GitHub PAT for private repositories |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server endpoint |
| `OLLAMA_MODEL` | `llama3.2` | LLM model to use for answers |

## Supported file types

| Category | Extensions |
|---|---|
| Code | `.py` `.java` `.js` `.ts` `.kt` `.feature` `.karate` |
| Docs | `.md` `.txt` `.yaml` `.yml` `.json` |

## Stack

| Component | Tool |
|---|---|
| Orchestration | LangChain (LCEL) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (local, CPU) |
| Vector store | ChromaDB (local, persistent) |
| LLM | Ollama `llama3.2` (local) |
| Repo cloning | GitPython |

## Project structure

```
codebase-ai/
├── main.py              # CLI entry point (index / ask / list)
├── config.py            # All configuration and defaults
├── indexer/
│   ├── cloner.py        # Git clone with timeout + token injection
│   ├── parser.py        # File traversal and text chunking
│   └── embedder.py      # HuggingFace embeddings (cached)
├── store/
│   └── vector_store.py  # ChromaDB read/write + repo metadata
├── agent/
│   ├── retriever.py     # Similarity search + context formatting
│   └── chain.py         # LangChain RAG chain (Ollama LLM)
├── data/
│   ├── repos/           # Cloned repos (git-ignored)
│   └── chroma/          # Persistent vector DB (git-ignored)
├── docs/
│   ├── architecture.md  # System design and improvement ideas
│   └── installation.md  # Step-by-step setup including accounts
├── .env.example
├── .gitignore
└── requirements.txt
```

## Docs

- [Installation guide](docs/installation.md) — accounts to create, tokens, dependencies, troubleshooting
- [Architecture](docs/architecture.md) — system design, component breakdown, and improvement ideas
