#!/usr/bin/env bash
# Tests for sanitize.py: personal emails in files and in commit metadata.
#
#   .github/scripts/test-sanitize.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SAN="$ROOT/.github/scripts/sanitize.py"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

PASS=0; FAILN=0
check() { # name expected actual
  if [ "$2" = "$3" ]; then PASS=$((PASS + 1)); echo "ok   $1"
  else FAILN=$((FAILN + 1)); echo "FAIL $1: expected [$2], got [$3]"; fi
}
scan() { python3 "$SAN" --check "$@" >/dev/null 2>&1 && echo clean || echo flagged; }

# Built at run time, so this file itself stays clean for the scanner.
PERSONAL="$(printf '%s@%s' jane.doe corp-mail.com)"
mkdir -p "$WORK/files"
printf 'Write to %s for access\n' "$PERSONAL" >"$WORK/files/personal.md"
check "flags a personal email in a file" flagged "$(scan "$WORK/files/personal.md")"
printf 'Use name@example.com, a@example.org or 1+bot@users.noreply.github.com\n' >"$WORK/files/ok.md"
check "allows example and noreply addresses" clean "$(scan "$WORK/files/ok.md")"
printf 'Questions: support@mutagent.io or security@mutagent.io\n' >"$WORK/files/role.md"
check "allows role addresses" clean "$(scan "$WORK/files/role.md")"

repo() { # dir author-email message
  git init -q "$1"
  printf 'x\n' >"$1/f.md"
  git -C "$1" add f.md
  git -C "$1" -c user.name=Someone -c user.email="$2" commit -q -m "$3"
}
repo "$WORK/r1" "$PERSONAL" "first"
check "--git flags a personal author email" flagged "$(scan --git "$WORK/r1")"
repo "$WORK/r2" 1+someone@users.noreply.github.com "first"
check "--git passes a noreply author" clean "$(scan --git "$WORK/r2")"
repo "$WORK/r4" factory@mutagent.io "first"
check "--git passes the project's author address" clean "$(scan --git "$WORK/r4")"
repo "$WORK/r5" "$(printf '%s@%s' factory2 mutagent.io)" "first"
check "--git flags any other address at that domain" flagged "$(scan --git "$WORK/r5")"
repo "$WORK/r3" 1+someone@users.noreply.github.com "token ghp_$(printf 'a%.0s' $(seq 30))"
check "--git flags a token in a commit message" flagged "$(scan --git "$WORK/r3")"

echo "$PASS passed, $FAILN failed"
[ "$FAILN" -eq 0 ]
