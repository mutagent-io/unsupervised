#!/usr/bin/env bash
# Build the release assets: the skill tarball and the release notes.
#
#   build-release.sh --tag v<version> --out <dir>
#
# Writes <dir>/unsupervised-v<version>.tar.gz (unpacks to unsupervised/, the skill
# a user installs; no CI or eval files) and <dir>/release-notes.md (the CHANGELOG
# entry for that version). Fails if the tag does not match SKILL.md's skill_version.
set -euo pipefail
TAG=""; OUT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --tag) TAG="${2:-}"; shift 2 ;;
    --out) OUT="${2:-}"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$TAG" ] && [ -n "$OUT" ] || { echo "usage: build-release.sh --tag v<version> --out <dir>" >&2; exit 2; }
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VERSION="$(sed -n 's/^  skill_version: "\(.*\)"$/\1/p' "$ROOT/SKILL.md")"
if [ "$TAG" != "v$VERSION" ]; then
  echo "tag $TAG does not match SKILL.md skill_version $VERSION" >&2
  exit 1
fi

mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
mkdir "$STAGE/unsupervised"
(cd "$ROOT" && cp -R SKILL.md AGENTS.md README.md LICENSE CHANGELOG.md references assets scripts agents .claude-plugin \
  "$STAGE/unsupervised/")
ASSET="$OUT/unsupervised-$TAG.tar.gz"
tar -czf "$ASSET" -C "$STAGE" unsupervised

{
  echo "# unsupervised $TAG"
  echo
  awk -v ver="$VERSION" '
    /^## \[/ { if (on) exit; if (index($0, "[" ver "]")) { on = 1; next } }
    on { print }
  ' "$ROOT/CHANGELOG.md"
} >"$OUT/release-notes.md"

echo "$ASSET"
