#!/usr/bin/env python3
"""
repo-guide: RAG agent for codebase onboarding.

Usage:
  python main.py index <github_url>   Clone and index a repo
  python main.py ask "<question>"     Ask a question about indexed repos
  python main.py list                 List indexed repos
"""
import sys


def cmd_index(url: str) -> None:
    from indexer.cloner import clone_repo, CloneTimeoutError, repo_name_from_url
    from indexer.parser import parse_repo
    from store.vector_store import delete_repo_docs, index_documents, save_repo_meta
    import git

    print(f"[index] Cloning {url} …")
    try:
        repo_path = clone_repo(url)
    except CloneTimeoutError:
        print(f"[error] Clone timed out after 30 s: {url}")
        sys.exit(1)
    except git.GitCommandError as exc:
        print(f"[error] Git error while cloning {url}:\n  {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"[error] Unexpected error cloning {url}:\n  {exc}")
        sys.exit(1)

    print(f"[index] Parsing files …")
    docs = parse_repo(repo_path, url)
    if not docs:
        print("[warn] No supported files found in this repo.")
        return

    repo_name = repo_name_from_url(url)
    print(f"[index] Removing old vectors for '{repo_name}' (if any) …")
    delete_repo_docs(repo_name)

    print(f"[index] Embedding and storing {len(docs)} chunks …")
    count = index_documents(docs)

    # Count unique files
    unique_files = len({d.metadata["file_path"] for d in docs})
    save_repo_meta(repo_name, url, unique_files)

    print(f"[done]  Indexed {unique_files} files → {count} chunks stored.")


def cmd_ask(question: str) -> None:
    from agent.chain import ask

    print(f"[ask] Querying repos …\n")
    answer = ask(question)
    print(answer)


def cmd_list() -> None:
    from store.vector_store import list_repos

    repos = list_repos()
    if not repos:
        print("No repos indexed yet. Run `python main.py index <github_url>`.")
        return

    print(f"{'Repo':<40} {'Files':>6}  {'Indexed at'}")
    print("-" * 70)
    for r in repos:
        name = r.get("repo_url", "unknown")
        files = r.get("file_count", "?")
        ts = r.get("indexed_at", "unknown")
        print(f"{name:<40} {files:>6}  {ts}")


def main() -> None:
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    command = args[0]

    if command == "index":
        if len(args) < 2:
            print("[error] Usage: python main.py index <github_url>")
            sys.exit(1)
        cmd_index(args[1])

    elif command == "ask":
        if len(args) < 2:
            print('[error] Usage: python main.py ask "<question>"')
            sys.exit(1)
        cmd_ask(args[1])

    elif command == "list":
        cmd_list()

    else:
        print(f"[error] Unknown command '{command}'. Use: index | ask | list")
        sys.exit(1)


if __name__ == "__main__":
    main()
