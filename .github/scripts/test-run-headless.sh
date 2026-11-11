#!/usr/bin/env bash
# Tests for scripts/run-headless.sh against a fake `architech` on PATH, so they
# run anywhere (CI included) without the product or a model.
#
#   .github/scripts/test-run-headless.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$ROOT/scripts/run-headless.sh"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/bin" "$WORK/project"
# Hold stdin open the way an agent's shell does (a FIFO opened read-write never
# reaches end-of-file), so the fake can tell whether the script closed it.
mkfifo "$WORK/stdin"; exec 0<>"$WORK/stdin"

# The fake reads FAKE_MODE and behaves like one headless turn.
cat >"$WORK/bin/architech" <<'FAKE'
#!/usr/bin/env bash
[ "${1:-}" = "-p" ] || { echo "fake: expected -p" >&2; exit 64; }
# stdin must be closed: a read hits end-of-file at once instead of timing out
read -r -t 1 _line; [ $? -gt 128 ] && { echo "fake: stdin left open" >&2; exit 65; }
case "${FAKE_MODE:-done}" in
  done)    printf 'working\n\nVERDICT: DONE\n' ;;
  blocked) printf 'VERDICT: BLOCKED which database?\n' ;;
  failed)  printf 'VERDICT: FAILED tests red\n'; exit 1 ;;
  none)    printf 'I answered without a verdict line\n' ;;
  crash)   echo "provider error" >&2; exit 3 ;;
  pwd)     pwd; printf 'VERDICT: DONE\n' ;;
  prompt)  printf '%s\nVERDICT: DONE\n' "$2" ;;
  hang)    sleep 300 & echo $! >"$FAKE_PIDFILE"; wait ;;   # a child that outlives a naive kill
esac
FAKE
chmod +x "$WORK/bin/architech"
export PATH="$WORK/bin:$PATH"

PASS=0; FAILN=0
check() { # name expected actual
  if [ "$2" = "$3" ]; then PASS=$((PASS + 1)); echo "ok   $1"
  else FAILN=$((FAILN + 1)); echo "FAIL $1: expected [$2], got [$3]"; fi
}
verdict() { FAKE_MODE="$1" "$SCRIPT" --cwd "$WORK/project" --prompt "hello" --timeout "${2:-30}" --run "$WORK/run-$1" | sed 's/.* verdict=//'; }

check "DONE on a last-line verdict"        DONE       "$(verdict "done")"
check "BLOCKED keeps its reason"           BLOCKED    "$(verdict blocked)"
check "FAILED on a FAILED verdict"         FAILED     "$(verdict failed)"
check "NO_VERDICT on exit 0 without one"   NO_VERDICT "$(verdict none)"
check "FAILED on a non-zero exit"          FAILED     "$(verdict crash)"
check "rc.txt records the exit code"       3          "$(cat "$WORK/run-crash/rc.txt")"
check "err.txt keeps stderr"               "provider error" "$(cat "$WORK/run-crash/err.txt")"

FAKE_MODE='pwd' "$SCRIPT" --cwd "$WORK/project" --prompt x --run "$WORK/run-pwd" >/dev/null
check "runs from --cwd" "$(cd "$WORK/project" && pwd -P)" "$(cd "$(head -n1 "$WORK/run-pwd/out.txt")" && pwd -P)"

printf 'line one\nline two\n' >"$WORK/brief.md"
FAKE_MODE=prompt "$SCRIPT" --cwd "$WORK/project" --brief "$WORK/brief.md" --run "$WORK/run-brief" >/dev/null
check "passes the brief file as the prompt" "line one|line two" "$(head -n2 "$WORK/run-brief/out.txt" | paste -sd'|' -)"

export FAKE_PIDFILE="$WORK/grandchild.pid"
start=$(date +%s)
check "TIMEOUT at the cap" TIMEOUT "$(verdict hang 2)"
check "rc 124 at the cap" 124 "$(cat "$WORK/run-hang/rc.txt")"
elapsed=$(( $(date +%s) - start ))
check "the cap is honoured (under 15 s)" yes "$([ "$elapsed" -lt 15 ] && echo yes || echo "no (${elapsed}s)")"
sleep 1
check "nothing left running after the cap" gone "$(kill -0 "$(cat "$FAKE_PIDFILE")" 2>/dev/null && echo alive || echo gone)"

check "rejects a missing --cwd"     2 "$("$SCRIPT" --prompt x >/dev/null 2>&1; echo $?)"
check "rejects a non-numeric cap"   2 "$("$SCRIPT" --cwd "$WORK/project" --prompt x --timeout 1m >/dev/null 2>&1; echo $?)"
check "rejects a missing brief"     2 "$("$SCRIPT" --cwd "$WORK/project" --brief "$WORK/nope.md" >/dev/null 2>&1; echo $?)"
check "rejects no prompt at all"    2 "$("$SCRIPT" --cwd "$WORK/project" >/dev/null 2>&1; echo $?)"
check "rejects an unknown argument" 2 "$("$SCRIPT" --cwd "$WORK/project" --prompt x --bogus >/dev/null 2>&1; echo $?)"

echo "$PASS passed, $FAILN failed"
[ "$FAILN" -eq 0 ]
