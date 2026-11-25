#!/usr/bin/env bash
# Dry run of the release build: the tarball and notes the release job publishes.
#
#   .github/scripts/test-build-release.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/.github/scripts/build-release.sh"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
VERSION="$(sed -n 's/^  skill_version: "\(.*\)"$/\1/p' "$ROOT/SKILL.md")"

PASS=0; FAILN=0
check() { # name expected actual
  if [ "$2" = "$3" ]; then PASS=$((PASS + 1)); echo "ok   $1"
  else FAILN=$((FAILN + 1)); echo "FAIL $1: expected [$2], got [$3]"; fi
}

out="$("$BUILD" --tag "v$VERSION" --out "$WORK/dist" 2>&1)" || true
ASSET="$WORK/dist/unsupervised-v$VERSION.tar.gz"
check "builds unsupervised-v<version>.tar.gz" yes "$([ -f "$ASSET" ] && echo yes || echo "no: $out")"

if [ -f "$ASSET" ]; then
  mkdir -p "$WORK/x" && tar -xzf "$ASSET" -C "$WORK/x"
  check "unpacks to one unsupervised/ folder" "unsupervised" "$(ls "$WORK/x")"
  for f in SKILL.md AGENTS.md README.md LICENSE CHANGELOG.md references/dispatch.md references/install.md \
           assets/icon.png assets/brief-template.md scripts/run-headless.sh agents/openai.yaml \
           .claude-plugin/plugin.json .claude-plugin/marketplace.json; do
    check "ships $f" yes "$([ -f "$WORK/x/unsupervised/$f" ] && echo yes || echo no)"
  done
  check "the runner stays executable" yes "$([ -x "$WORK/x/unsupervised/scripts/run-headless.sh" ] && echo yes || echo no)"
  extras=""
  for d in .github evals .git; do
    if [ -e "$WORK/x/unsupervised/$d" ]; then extras="$extras $d"; fi
  done
  check "no CI or eval files in the skill tarball" "" "$extras"
fi

NOTES="$WORK/dist/release-notes.md"
check "notes start with the release title" "# unsupervised v$VERSION" "$(head -n1 "$NOTES" 2>/dev/null)"
check "notes carry the CHANGELOG entry" yes "$(grep -q '^### ' "$NOTES" 2>/dev/null && echo yes || echo no)"
check "notes drop the CHANGELOG heading" yes \
  "$([ -s "$NOTES" ] && ! grep -qE '^## \[|unreleased' "$NOTES" && echo yes || echo no)"

check "refuses a tag that does not match skill_version" 1 \
  "$("$BUILD" --tag v9.9.9 --out "$WORK/bad" >/dev/null 2>&1; echo $?)"

echo "$PASS passed, $FAILN failed"
[ "$FAILN" -eq 0 ]
