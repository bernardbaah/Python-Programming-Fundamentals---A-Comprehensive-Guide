"""
sync_to_github.py — push key project files to GitHub after a book rebuild.

Usage (standalone):
    python .agents/scripts/sync_to_github.py

Called automatically at the end of build_pdf_elegant.py and build_book_elegant.py.

Requires the BERNARD_BAAH_PAT environment variable (a GitHub Personal Access Token
with repo write scope).  If the variable is absent the script prints a warning and
exits 0 so it never breaks a build.
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request

# ── Config ────────────────────────────────────────────────────────────────────
REPO     = "bernardbaah/Python-Programming-Fundamentals---A-Comprehensive-Guide"
BASE_URL = f"https://api.github.com/repos/{REPO}/contents"

# Files to sync: (local_path, repo_path, commit_message)
FILES_TO_SYNC = [
    ("app.py",         "app.py",         "chore: sync app.py after book rebuild"),
    ("viewer.html",    "viewer.html",     "chore: sync viewer.html after book rebuild"),
    ("README.md",      "README.md",       "chore: sync README.md after book rebuild"),
    (
        ".agents/scripts/build_pdf_elegant.py",
        ".agents/scripts/build_pdf_elegant.py",
        "chore: sync build_pdf_elegant.py after book rebuild",
    ),
    (
        ".agents/scripts/build_book_elegant.py",
        ".agents/scripts/build_book_elegant.py",
        "chore: sync build_book_elegant.py after book rebuild",
    ),
    (
        ".agents/scripts/sync_to_github.py",
        ".agents/scripts/sync_to_github.py",
        "chore: sync sync_to_github.py after book rebuild",
    ),
]


def _headers(pat: str) -> dict:
    return {
        "Authorization": f"token {pat}",
        "Accept":        "application/vnd.github.v3+json",
        "Content-Type":  "application/json",
    }


def _get_sha(repo_path: str, pat: str) -> str | None:
    """Return the current blob SHA for repo_path, or None if the file doesn't exist."""
    url = f"{BASE_URL}/{repo_path}"
    req = urllib.request.Request(url, headers=_headers(pat))
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None          # file doesn't exist yet — will be created
        raise


def _push_file(local_path: str, repo_path: str, message: str, pat: str) -> bool:
    """Create or update a single file in the repo.  Returns True on success."""
    if not os.path.exists(local_path):
        print(f"  ⚠  skipped (not found locally): {local_path}")
        return False

    with open(local_path, "rb") as fh:
        content = base64.b64encode(fh.read()).decode()

    sha = _get_sha(repo_path, pat)

    payload: dict = {"message": message, "content": content}
    if sha:
        payload["sha"] = sha   # required for updates; absent for new files

    data = json.dumps(payload).encode()
    url  = f"{BASE_URL}/{repo_path}"
    req  = urllib.request.Request(url, data=data, headers=_headers(pat), method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            action = "updated" if sha else "created"
            print(f"  ✓ {repo_path}  [{action}]  →  {result['content']['html_url']}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ✗ {repo_path}: HTTP {e.code}  {body[:300]}")
        return False


def sync(files: list[tuple[str, str, str]] | None = None) -> bool:
    """
    Push *files* (or FILES_TO_SYNC) to GitHub.

    Returns True if every file succeeded, False otherwise.
    Prints a warning and returns True when the PAT is missing (non-fatal).
    """
    pat = os.environ.get("BERNARD_BAAH_PAT", "").strip()
    if not pat:
        print(
            "\n⚠  BERNARD_BAAH_PAT not set — skipping GitHub sync.\n"
            "   Set the secret in Replit and rebuild to enable auto-sync."
        )
        return True   # not a build failure

    targets = files or FILES_TO_SYNC
    print(f"\n── GitHub sync → {REPO} ──")
    results = [_push_file(lp, rp, msg, pat) for lp, rp, msg in targets]
    ok = all(results)
    if ok:
        print(f"── sync complete ({len(results)} file(s)) ──\n")
    else:
        failed = sum(1 for r in results if not r)
        print(f"── sync finished with {failed} failure(s) ──\n")
    return ok


# ── Standalone entry-point ────────────────────────────────────────────────────
if __name__ == "__main__":
    success = sync()
    sys.exit(0 if success else 1)
