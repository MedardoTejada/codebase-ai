import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPOS_DIR = DATA_DIR / "repos"
CHROMA_DIR = DATA_DIR / "chroma"

REPOS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

CLONE_TIMEOUT = 30

CHROMA_COLLECTION = "repo_guide"

SUPPORTED_EXTENSIONS = {
    ".py", ".java", ".js", ".ts", ".kt",
    ".feature", ".karate",
    ".md", ".txt", ".yaml", ".yml", ".json",
}

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
