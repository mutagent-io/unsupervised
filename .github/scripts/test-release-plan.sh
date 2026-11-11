#!/usr/bin/env bash
# Dry run of the Release workflow's decision against a local bare "origin", for
# every way a version bump can reach main.
#
#   .github/scripts/test-release-plan.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PLAN="$ROOT/.github/scripts/release-plan.sh"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.com
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

PASS=0; FAILN=0
check() { # name expected actual
  if [ "$2" = "$3" ]; then PASS=$((PASS + 1)); echo "ok   $1"
  else FAILN=$((FAILN + 1)); echo "FAIL $1: expected [$2], got [$3]"; fi
}
set_version() { sed -i.bak "s/^  skill_version: \".*\"$/  skill_version: \"$1\"/" SKILL.md && rm -f SKILL.md.bak; }

# origin with v0.1.0 released; returns a working clone on main
setup() { # name
  local d="$WORK/$1"
  git init -q --bare -b main "$d/origin.git"
  git clone -q "$d/origin.git" "$d/dev" 2>/dev/null
  cd "$d/dev"
  git checkout -q -b main
  printf -- '---\nmetadata:\n  skill_version: "0.1.0"\n---\n' >SKILL.md
  git add SKILL.md && git commit -qm "release 0.1.0"
  git tag v0.1.0 && git push -q origin main v0.1.0
}
# what the workflow sees: a fresh checkout of main (full history, so a decision
# that peeks at earlier commits would show here), then the plan
plan() { # name
  local d="$WORK/$1"
  rm -rf "$d/ci" && git clone -q "$d/origin.git" "$d/ci" 2>/dev/null
  (cd "$d/ci" && "$PLAN" 2>/dev/null | paste -sd' ' -)
}
want="tag=v0.1.1 push_tag=true publish=true"

# (a) direct push: the bump, then another commit, pushed straight to main
setup a; set_version 0.1.1; git commit -qam "bump 0.1.1"; echo x >notes; git add notes; git commit -qm "docs"
git push -q origin main
check "(a) direct push, bump not last: releases v0.1.1" "$want" "$(plan a)"

# (b) squash merge: one commit on main holds the bump
setup b; git checkout -q -b feature; set_version 0.1.1; git commit -qam "bump"; echo x >notes; git add notes; git commit -qm docs
git checkout -q main; git merge -q --squash feature >/dev/null; git commit -qm "feature (squashed)"; git push -q origin main
check "(b) squash merge: releases v0.1.1" "$want" "$(plan b)"

# (c) merge commit
setup c; git checkout -q -b feature; set_version 0.1.1; git commit -qam "bump"; echo x >notes; git add notes; git commit -qm docs
git checkout -q main; echo y >other; git add other; git commit -qm "meanwhile on main"
git merge -q --no-ff -m "Merge feature" feature; git push -q origin main
check "(c) merge commit: releases v0.1.1" "$want" "$(plan c)"

# (d) rebase merge: the bump commit followed by another, replayed onto main
setup d; echo y >other; git add other; git commit -qm "meanwhile on main"; git push -q origin main
git checkout -q -b feature HEAD~1; set_version 0.1.1; git commit -qam "bump"; echo x >notes; git add notes; git commit -qm docs
git rebase -q main; git checkout -q main; git merge -q --ff-only feature; git push -q origin main
check "(d) rebase merge, bump not last: releases v0.1.1" "$want" "$(plan d)"

# no new version: v0.1.0 already exists on origin
setup e; echo x >notes; git add notes; git commit -qm docs; git push -q origin main
check "unchanged version (tag exists): no release" "publish=false" "$(plan e)"

# the first content of a new repo: no tag yet, several commits
d="$WORK/f"; git init -q --bare -b main "$d/origin.git"; git clone -q "$d/origin.git" "$d/dev" 2>/dev/null; cd "$d/dev"
git checkout -q -b main; printf -- '---\nmetadata:\n  skill_version: "0.1.0"\n---\n' >SKILL.md
git add SKILL.md; git commit -qm one; echo x >notes; git add notes; git commit -qm two; git push -q origin main
check "first push of a new repo: releases v0.1.0" "tag=v0.1.0 push_tag=true publish=true" "$(plan f)"

# workflow_dispatch with an existing tag, and a malformed one
cd "$WORK/e/dev"
check "dispatch v0.1.0: publish without a new tag" "tag=v0.1.0 push_tag=false publish=true" "$("$PLAN" v0.1.0 2>/dev/null | paste -sd' ' -)"
check "dispatch rejects a malformed tag" 1 "$("$PLAN" 'v1; rm -rf /' >/dev/null 2>&1; echo $?)"

echo "$PASS passed, $FAILN failed"
[ "$FAILN" -eq 0 ]
