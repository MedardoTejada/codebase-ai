import shutil
import signal
from pathlib import Path
from urllib.parse import urlparse

import git

from config import REPOS_DIR, GITHUB_TOKEN, CLONE_TIMEOUT


class CloneTimeoutError(Exception):
    pass


def _timeout_handler(signum, frame):
    raise CloneTimeoutError("Clone timed out after 30 seconds")


def repo_name_from_url(url: str) -> str:
    """Derive a filesystem-safe name from a GitHub URL."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    # e.g. /owner/repo -> owner__repo
    parts = [p for p in path.split("/") if p]
    return "__".join(parts)


def clone_repo(url: str) -> Path:
    """
    Clone a GitHub repo into data/repos/<owner__repo>.
    If the directory already exists it is removed first (full reindex).
    Returns the local path.
    Raises CloneTimeoutError or git.GitCommandError on failure.
    """
    name = repo_name_from_url(url)
    dest = REPOS_DIR / name

    if dest.exists():
        shutil.rmtree(dest)

    clone_url = _inject_token(url)

    # Use SIGALRM for timeout on Unix
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(CLONE_TIMEOUT)
    try:
        git.Repo.clone_from(clone_url, dest)
    finally:
        signal.alarm(0)

    return dest


def _inject_token(url: str) -> str:
    """Inject GITHUB_TOKEN into HTTPS URL if available."""
    if not GITHUB_TOKEN:
        return url
    parsed = urlparse(url)
    if parsed.scheme in ("http", "https"):
        authed = parsed._replace(
            netloc=f"{GITHUB_TOKEN}@{parsed.netloc}"
        )
        return authed.geturl()
    return url
