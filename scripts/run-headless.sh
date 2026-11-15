#!/usr/bin/env bash
# run-headless.sh: run one headless Architech turn for a coding agent and grade it.
#
#   run-headless.sh --cwd /abs/project (--brief /abs/brief.md | --prompt "text")
#                   [--timeout 900] [--run /abs/run-dir]
#
# Writes RUN/out.txt (answer), RUN/err.txt, RUN/rc.txt, RUN/verdict.txt, RUN/pgid.txt
# (Architech's process group, for cleanup after a hard kill of this script) and prints
# one line: run=<dir> rc=<code> verdict=<DONE|BLOCKED|FAILED|NO_VERDICT|TIMEOUT|INTERRUPTED>.
# Stdin is closed for the child. At the cap, or when this script is stopped (TERM, INT,
# HUP), the child's whole process group is stopped, so nothing keeps running unwatched.
# Exits 0 once a verdict is written (read the verdict), 128+signal when interrupted,
# 2 on bad arguments. Refuses a /ship or /execute prompt: both can merge, and a
# headless run never merges.
set -euo pipefail
CWD=""; BRIEF=""; PROMPT=""; CAP=900; RUN=""; PID=""
while [ $# -gt 0 ]; do
  case "$1" in
    --cwd) CWD="${2:-}"; shift 2 ;;
    --brief) BRIEF="${2:-}"; shift 2 ;;
    --prompt) PROMPT="${2:-}"; shift 2 ;;
    --timeout) CAP="${2:-}"; shift 2 ;;
    --run) RUN="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
if [ -z "$CWD" ] || [ ! -d "$CWD" ]; then echo "--cwd must be an existing directory" >&2; exit 2; fi
case "$CAP" in ''|*[!0-9]*) echo "--timeout takes whole seconds" >&2; exit 2 ;; esac
if [ "$CAP" -lt 1 ]; then echo "--timeout must be at least 1 second" >&2; exit 2; fi
if [ -n "$BRIEF" ]; then
  [ -f "$BRIEF" ] || { echo "brief not found: $BRIEF" >&2; exit 2; }
  PROMPT="$(cat "$BRIEF")"
fi
[ -n "$PROMPT" ] || { echo "give --brief or --prompt" >&2; exit 2; }
case "$(printf '%s\n' "$PROMPT" | awk 'NF { print $1; exit }')" in
  /ship) echo "refused: /ship merges, and a headless run never merges; run it interactively" >&2; exit 2 ;;
  /execute) echo "refused: /execute merges as your merge rules allow, and a headless run never merges; run it interactively" >&2; exit 2 ;;
esac
command -v architech >/dev/null 2>&1 || { echo "architech is not on PATH" >&2; exit 2; }
RUN="${RUN:-$(mktemp -d)}"; mkdir -p "$RUN"; RUN="$(cd "$RUN" && pwd)"

stop_group() {  # TERM the child's process group, wait up to 5 s, then KILL it
  kill -TERM -- "-$PID" 2>/dev/null || return 0
  for _ in 1 2 3 4 5; do
    kill -0 -- "-$PID" 2>/dev/null || return 0
    sleep 1
  done
  kill -KILL -- "-$PID" 2>/dev/null || true
}
finish() {  # rc verdict
  echo "$1" >"$RUN/rc.txt"
  echo "$2" >"$RUN/verdict.txt"
  printf 'run=%s rc=%s verdict=%s\n' "$RUN" "$1" "$2"
}
on_signal() {  # signal-number
  trap - HUP INT TERM
  [ -n "$PID" ] && stop_group
  finish "$((128 + $1))" INTERRUPTED
  exit "$((128 + $1))"
}
trap 'on_signal 1' HUP
trap 'on_signal 2' INT
trap 'on_signal 15' TERM

set -m  # the child runs in its own process group, so one signal stops all of it
( cd "$CWD" && exec architech -p "$PROMPT" </dev/null >"$RUN/out.txt" 2>"$RUN/err.txt" ) &
PID=$!
echo "$PID" >"$RUN/pgid.txt"  # the subshell leads its own group: its PID is the group ID
set +m  # job control for the launch only: the polling sleeps stay in this script's group,
        # so a terminal Ctrl-C reaches this script and its INT trap
SECS=0; RC=""
while kill -0 "$PID" 2>/dev/null; do
  if [ "$SECS" -ge "$CAP" ]; then
    stop_group
    RC=124
    break
  fi
  sleep 1; SECS=$((SECS + 1))
done
if [ -z "$RC" ]; then set +e; wait "$PID"; RC=$?; set -e; fi
trap - HUP INT TERM

LAST="$(grep -v '^[[:space:]]*$' "$RUN/out.txt" 2>/dev/null | tail -n 1 || true)"
if [ "$RC" -gt 128 ] && [ "$RC" -lt 160 ]; then
  V=INTERRUPTED            # Architech died by a signal: stopped from outside, not a failure
else
  case "$RC|$LAST" in
    "124|"*) V=TIMEOUT ;;
    "0|VERDICT: DONE"*) V=DONE ;;
    "0|VERDICT: BLOCKED"*) V=BLOCKED ;;
    *"|VERDICT: FAILED"*) V=FAILED ;;
    "0|"*) V=NO_VERDICT ;;   # the turn ended without the brief's last line: read out.txt
    *) V=FAILED ;;           # non-zero exit: read err.txt first
  esac
fi
finish "$RC" "$V"
