#!/usr/bin/env bash
# run-headless.sh: run one headless Architech turn for a coding agent and grade it.
#
#   run-headless.sh --cwd /abs/project (--brief /abs/brief.md | --prompt "text")
#                   [--timeout 900] [--run /abs/run-dir]
#
# Writes RUN/out.txt (answer), RUN/err.txt, RUN/rc.txt, RUN/verdict.txt and prints
# one line: run=<dir> rc=<code> verdict=<DONE|BLOCKED|FAILED|NO_VERDICT|TIMEOUT>.
# Stdin is closed for the child, and the wall-clock cap stops the whole process
# group, so nothing keeps running after the cap. Needs only bash and architech.
set -euo pipefail
CWD=""; BRIEF=""; PROMPT=""; CAP=900; RUN=""
while [ $# -gt 0 ]; do
  case "$1" in
    --cwd) CWD="${2:-}"; shift 2 ;;
    --brief) BRIEF="${2:-}"; shift 2 ;;
    --prompt) PROMPT="${2:-}"; shift 2 ;;
    --timeout) CAP="${2:-}"; shift 2 ;;
    --run) RUN="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$CWD" ] && [ -d "$CWD" ] || { echo "--cwd must be an existing directory" >&2; exit 2; }
case "$CAP" in ''|*[!0-9]*) echo "--timeout takes whole seconds" >&2; exit 2 ;; esac
if [ -n "$BRIEF" ]; then
  [ -f "$BRIEF" ] || { echo "brief not found: $BRIEF" >&2; exit 2; }
  PROMPT="$(cat "$BRIEF")"
fi
[ -n "$PROMPT" ] || { echo "give --brief or --prompt" >&2; exit 2; }
command -v architech >/dev/null 2>&1 || { echo "architech is not on PATH" >&2; exit 2; }
RUN="${RUN:-$(mktemp -d)}"; mkdir -p "$RUN"

set -m  # the child runs in its own process group, so the cap can stop all of it
( cd "$CWD" && exec architech -p "$PROMPT" </dev/null >"$RUN/out.txt" 2>"$RUN/err.txt" ) &
PID=$!
SECS=0; RC=""
while kill -0 "$PID" 2>/dev/null; do
  if [ "$SECS" -ge "$CAP" ]; then
    kill -TERM -- "-$PID" 2>/dev/null || true
    sleep 5
    kill -KILL -- "-$PID" 2>/dev/null || true
    RC=124
    break
  fi
  sleep 2; SECS=$((SECS + 2))
done
if [ -z "$RC" ]; then set +e; wait "$PID"; RC=$?; set -e; fi
echo "$RC" >"$RUN/rc.txt"

LAST="$(grep -v '^[[:space:]]*$' "$RUN/out.txt" 2>/dev/null | tail -n 1 || true)"
case "$RC|$LAST" in
  "124|"*) V=TIMEOUT ;;
  "0|VERDICT: DONE"*) V=DONE ;;
  "0|VERDICT: BLOCKED"*) V=BLOCKED ;;
  *"|VERDICT: FAILED"*) V=FAILED ;;
  "0|"*) V=NO_VERDICT ;;   # the turn ended without the brief's last line: read out.txt
  *) V=FAILED ;;           # non-zero exit: read err.txt first
esac
echo "$V" >"$RUN/verdict.txt"
printf 'run=%s rc=%s verdict=%s\n' "$RUN" "$RC" "$V"
