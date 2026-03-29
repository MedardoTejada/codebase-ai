# Installation Guide

## Requirements

- Python 3.10 or higher
- macOS, Linux, or Windows (WSL recommended on Windows)
- ~2 GB disk space for the LLM model
- Internet connection for first run (to download embedding model and LLM)

---

## Step 1 — Accounts and tokens

### HuggingFace (required)

The embedding model (`all-MiniLM-L6-v2`) is downloaded from HuggingFace on first run. You need an account and an access token.

1. Create a free account at [huggingface.co](https://huggingface.co/join)
2. Go to **Settings → Access Tokens** ([huggingface.co/settings/tokens](https://huggingface.co/settings/tokens))
3. Click **New token** → choose **Read** role → copy the token (starts with `hf_`)
4. Add it to your `.env` file:
   ```
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
   ```

> Without this token, downloads still work but are rate-limited and slower. You may see a warning: `"You are sending unauthenticated requests to the HF Hub"` — this is harmless but not ideal.

### GitHub (optional — only for private repos)

If you want to index private repositories:

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Create a token with **Contents: Read** permission for the repos you need
3. Add it to your `.env` file:
   ```
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
   ```

Public repos work without any token.

---

## Step 2 — Install Ollama

Ollama runs the LLM locally on your machine.

**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS (Homebrew):**
```bash
brew install ollama
```

**Windows:** Download the installer from [ollama.com](https://ollama.com/download)

After installing, start the Ollama server:
```bash
ollama serve
```

Then download the default LLM (this is a ~2 GB download, do it once):
```bash
ollama pull llama3.2
```

Verify it works:
```bash
ollama list
```

You should see `llama3.2` in the list.

> Ollama must be running (`ollama serve`) every time you use repo-guide. On macOS, the desktop app starts it automatically.

---

## Step 3 — Clone and set up the project

```bash
git clone https://github.com/MedardoTejada/codebase-ai.git
cd codebase-ai
```

Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Step 4 — Configure environment

Copy the example env file:
```bash
cp .env.example .env
```

Edit `.env` and fill in your tokens:
```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx       # Required — HuggingFace token
GITHUB_TOKEN=                          # Optional — only for private repos
OLLAMA_BASE_URL=http://localhost:11434  # Default, change if Ollama runs elsewhere
OLLAMA_MODEL=llama3.2                  # Default model, can use llama3.1, mistral, etc.
```

---

## Step 5 — First run

The first time you index a repo, two things will be downloaded automatically:

1. **HuggingFace embedding model** (`all-MiniLM-L6-v2`, ~90 MB) — downloaded once, cached in `~/.cache/huggingface/`
2. **ChromaDB ONNX runtime** (~79 MB) — downloaded once, cached in `~/.cache/chroma/`

This only happens on the first run. Subsequent runs are fast.

```bash
python main.py index https://github.com/some/repo
```

---

## Dependency overview

| Package | Purpose |
|---|---|
| `langchain`, `langchain-core`, `langchain-text-splitters` | RAG chain orchestration and text splitting |
| `langchain-chroma` | ChromaDB integration for LangChain |
| `langchain-huggingface` | HuggingFace embeddings integration |
| `langchain-ollama` | Ollama LLM integration |
| `chromadb` | Local vector database |
| `sentence-transformers` | Loads and runs the embedding model locally |
| `gitpython` | Clones GitHub repositories |
| `python-dotenv` | Loads `.env` configuration |

---

## Troubleshooting

**`ModuleNotFoundError`** — Make sure your virtual environment is activated: `source .venv/bin/activate`

**`Connection refused` when asking questions** — Ollama is not running. Start it with `ollama serve`.

**`Permission denied (publickey)` on git push** — Your SSH key is not added to GitHub. See [GitHub SSH docs](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

**HuggingFace rate limit warning** — Add your `HF_TOKEN` to `.env` as described in Step 1.

**Clone timeout on large repos** — The default timeout is 30 seconds. For large repos, run the clone manually first or increase `CLONE_TIMEOUT` in `config.py`.
