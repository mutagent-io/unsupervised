#!/usr/bin/env python3
"""
Check that nothing private or machine-specific ships in this public repo.

The whole repository is the installed skill folder, so every text file is
scanned, not only the skill's markdown. Patterns are generic on purpose: a
public list of private names would publish the names it protects. Maintainers
run their own private list before each pull request (see CONTRIBUTING.md).

Usage:
    ./.github/scripts/sanitize.py --check           # files (CI)
    ./.github/scripts/sanitize.py --check <path>
    ./.github/scripts/sanitize.py --check --git     # commit authors, committers, messages
    ./.github/scripts/sanitize.py --check --git <repo>
"""
# Personal email addresses are flagged; these stay allowed: documentation
# domains, GitHub noreply addresses, and role mailboxes.

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()

# (label, regex). Each one is generic: shapes, not names.
LEAK_PATTERNS: list[tuple[str, str]] = [
    ("absolute home path", r"(?<![\w.~])/(?:Users|home)/[A-Za-z0-9._-]+/"),
    ("Windows user path", r"[A-Za-z]:\\Users\\"),
    ("macOS temp path", r"/var/folders/[a-z0-9_]{2}/"),
    ("private key block", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("GitHub token", r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    ("API key", r"\b(?:sk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|xox[abpr]-[A-Za-z0-9-]{10,})"),
    ("AWS key id", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("bearer token", r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{24,}"),
    ("assignment of a secret", r"(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"\s<>]{12,}['\"]"),
]
# Links that leave the repository are checked by check_skill.py, which resolves them.
LEAK_RE = [(label, re.compile(rx)) for label, rx in LEAK_PATTERNS]

EMAIL_RE = re.compile(r"(?<![\w.+-])([A-Za-z0-9._%+-]+)@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,})")
ALLOWED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net", "users.noreply.github.com"}
ROLE_MAILBOXES = {"noreply", "no-reply", "hello", "support", "team", "security", "contact",
                  "info", "oss", "opensource", "legal", "privacy"}
# The project's commit author address, allowed exactly (no other address at its domain).
ALLOWED_EMAILS = {"factory@mutagent.io"}


def personal_emails(line: str) -> list[str]:
    found = []
    for local, domain in EMAIL_RE.findall(line):
        address = f"{local}@{domain}".lower()
        if address in ALLOWED_EMAILS or domain.lower() in ALLOWED_EMAIL_DOMAINS or local.lower() in ROLE_MAILBOXES:
            continue
        found.append(f"{local}@{domain}")
    return found


def line_hits(line: str) -> list[str]:
    labels = [label for label, rx in LEAK_RE if rx.search(line)]
    if personal_emails(line):
        labels.append("personal email")
    return labels

SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__"}
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".gz", ".zip"}


def files_in(scope: Path) -> list[Path]:
    if scope.is_file():
        return [scope]
    out = []
    for p in sorted(scope.rglob("*")):
        if not p.is_file() or p.resolve() == SELF:
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(scope).parts):
            continue
        if p.suffix.lower() in BINARY_SUFFIXES:
            continue
        out.append(p)
    return out


def scan(files: list[Path]) -> list[tuple[str, int, str, str]]:
    hits = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for label in line_hits(line):
                hits.append((str(path), lineno, label, line.strip()[:160]))
    return hits


def scan_git(repo: Path) -> tuple[int, list[tuple[str, int, str, str]]]:
    """Scan every commit's author, committer and message."""
    out = subprocess.run(
        ["git", "-C", str(repo), "log", "--all", "--format=%H%x00%an <%ae>%x00%cn <%ce>%x00%B%x1e"],
        check=True, capture_output=True, text=True).stdout
    hits, commits = [], [c for c in out.split("\x1e") if c.strip()]
    for commit in commits:
        sha, author, committer, body = commit.strip("\n").split("\x00", 3)
        for field, text in (("author", author), ("committer", committer), ("message", body)):
            for lineno, line in enumerate(text.splitlines(), 1):
                for label in line_hits(line):
                    hits.append((f"commit {sha[:12]} {field}", lineno, label, line.strip()[:160]))
    return len(commits), hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Check for private or machine-specific content.")
    parser.add_argument("scope", nargs="?", default=str(REPO_ROOT))
    parser.add_argument("--check", action="store_true", help="verify only (the default; kept for CI parity)")
    parser.add_argument("--git", action="store_true", help="scan commit metadata instead of files")
    args = parser.parse_args()

    scope = Path(args.scope).resolve()
    if not scope.exists():
        print(f"ERROR: scope does not exist: {scope}", file=sys.stderr)
        return 2
    if args.git:
        count, hits = scan_git(scope)
        what = f"{count} commit(s)"
    else:
        files = files_in(scope)
        base = scope if scope.is_dir() else scope.parent
        hits = [(str(Path(p).relative_to(base)), n, label, line) for p, n, label, line in scan(files)]
        what = f"{len(files)} file(s)"
    if hits:
        print(f"ERROR: {len(hits)} leak match(es):", file=sys.stderr)
        for where, lineno, label, line in hits:
            print(f"  {where}:{lineno}: [{label}] {line}", file=sys.stderr)
        return 1
    print(f"OK: {what} scanned, no leaks detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
