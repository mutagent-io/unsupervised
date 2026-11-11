#!/usr/bin/env bash
# Decide what the Release workflow does, from the checked-out commit.
#
#   release-plan.sh [<tag>]     # a tag = the workflow_dispatch input
#
# Prints key=value lines (tag, push_tag, publish), appended to $GITHUB_OUTPUT
# when that is set. Needs `origin` to be reachable for the tag lookup.
set -euo pipefail
INPUT_TAG="${1:-}"
emit() { if [ -n "${GITHUB_OUTPUT:-}" ]; then printf '%s\n' "$@" >>"$GITHUB_OUTPUT"; fi; printf '%s\n' "$@"; }
read_version() { sed -n 's/^  skill_version: "\(.*\)"$/\1/p'; }
version=$(read_version < SKILL.md)
if [[ -n "$INPUT_TAG" ]]; then
  [[ "$INPUT_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "::error::tag must look like v1.2.3" >&2; exit 1; }
  emit "tag=$INPUT_TAG" push_tag=false publish=true
  exit 0
fi
# Release whenever this version has no tag on origin yet. Nothing here looks at
# earlier commits, so every way of reaching main (direct push, squash, merge
# commit, rebase merge) releases a new version exactly once.
tag="v$version"
if git ls-remote --exit-code --tags origin "refs/tags/$tag" >/dev/null; then
  echo "tag $tag already exists; nothing new to release (re-publish it with workflow_dispatch)" >&2
  emit publish=false; exit 0
fi
emit "tag=$tag" push_tag=true publish=true
