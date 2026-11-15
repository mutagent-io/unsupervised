#!/usr/bin/env bash
# Tests for scripts/run-headless.sh against a fake `architech` on PATH, so they
# run anywhere (CI included) without the product or a model.
#
#   .github/scripts/test-run-headless.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$ROOT/scripts/run-headless.sh"
WORK="$(mktemp -d)"
# On exit, stop any fake left by a failing case, then remove the scratch dir.
cleanup() {
  local f
  for f in "$WORK"/*.pid "$WORK"/*.pid.fake; do
    [ -s "$f" ] && kill -KILL "$(cat "$f")" 2>/dev/null || true
  done
  rm -rf "$WORK"
}
trap cleanup EXIT
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
  hang)    echo $$ >"$FAKE_PIDFILE.fake"                   # the fake itself, then
           sleep 300 & echo $! >"$FAKE_PIDFILE"; wait ;;   # a child that outlives a naive kill
esac
FAKE
chmod +x "$WORK/bin/architech"
# Fake-only PATH: the fake architech and system tools, never a real install.
TOOL_DIRS=""
for t in python3 tmux; do
  d="$(dirname "$(command -v "$t" 2>/dev/null || echo /usr/bin/x)")"
  [ -x "$d/architech" ] || TOOL_DIRS="$TOOL_DIRS:$d"   # never a dir that holds a real one
done
export PATH="$WORK/bin:/usr/bin:/bin:/usr/sbin:/sbin$TOOL_DIRS"

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

# The host stops the runner (a shell-call time limit, Ctrl-C, a closed terminal):
# the runner must stop Architech too and still leave a verdict behind.
for sig in TERM HUP INT; do
  pidfile="$WORK/grandchild-$sig.pid"
  set -m   # job control: the runner gets its own group and keeps INT, like a foreground run
  FAKE_MODE=hang FAKE_PIDFILE="$pidfile" "$SCRIPT" --cwd "$WORK/project" --prompt x \
    --timeout 600 --run "$WORK/run-sig-$sig" >/dev/null 2>&1 &
  runner=$!
  set +m
  for _ in $(seq 50); do [ -s "$pidfile" ] && break; sleep 0.2; done
  kill -"$sig" "$runner"
  wait "$runner" 2>/dev/null || true
  check "$sig to the runner: verdict INTERRUPTED" INTERRUPTED "$(cat "$WORK/run-sig-$sig/verdict.txt" 2>/dev/null)"
  check "$sig to the runner: rc.txt is 128+signal" "$((128 + $(kill -l "$sig")))" "$(cat "$WORK/run-sig-$sig/rc.txt" 2>/dev/null)"
  check "$sig to the runner: Architech's process tree is gone" gone \
    "$(kill -0 "$(cat "$pidfile" 2>/dev/null || echo 999999)" 2>/dev/null && echo alive || echo gone)"
done

# A real Ctrl-C from a terminal: the runner runs on a pty as its controlling
# terminal, and ^C written to the pty makes the terminal send SIGINT to whatever
# process group is in the foreground, exactly as a person pressing Ctrl-C does.
pidfile="$WORK/grandchild-ctrlc.pid"
ctrlc_exit="$(FAKE_MODE=hang FAKE_PIDFILE="$pidfile" python3 - "$SCRIPT" "$WORK/project" "$WORK/run-ctrlc" "$pidfile" <<'PY'
import os, pty, select, sys, time
script, project, run, pidfile = sys.argv[1:5]
pid, fd = pty.fork()
if pid == 0:
    os.execvp(script, [script, "--cwd", project, "--prompt", "x", "--timeout", "600", "--run", run])
deadline = time.time() + 15
while not (os.path.exists(pidfile) and os.path.getsize(pidfile)) and time.time() < deadline:
    time.sleep(0.2)
time.sleep(1.5)            # let the runner settle into its polling loop
os.write(fd, b"\x03")      # Ctrl-C, through the terminal
end = time.time() + 20
while time.time() < end:  # drain output until the runner closes the pty
    r, _, _ = select.select([fd], [], [], 0.5)
    if r:
        try:
            if not os.read(fd, 4096):
                break
        except OSError:
            break
    done, status = os.waitpid(pid, os.WNOHANG)
    if done:
        break
else:
    os.kill(pid, 9)
    done, status = os.waitpid(pid, 0)
if not done:
    done, status = os.waitpid(pid, 0)
print(os.waitstatus_to_exitcode(status))
PY
)"
sleep 1
check "Ctrl-C on a terminal: verdict INTERRUPTED" INTERRUPTED "$(cat "$WORK/run-ctrlc/verdict.txt" 2>/dev/null)"
check "Ctrl-C on a terminal: the runner exits 130" 130 "$ctrlc_exit"
for which in "$pidfile" "$pidfile.fake"; do
  check "Ctrl-C on a terminal: $(basename "$which") process gone" gone \
    "$(kill -0 "$(cat "$which" 2>/dev/null || echo 999999)" 2>/dev/null && echo alive || echo gone)"
done

(cd "$WORK" && FAKE_MODE="done" "$SCRIPT" --cwd "$WORK/project" --prompt x --run rel-run >/dev/null)
check "a relative --run lands beside the caller" DONE "$(cat "$WORK/rel-run/verdict.txt" 2>/dev/null)"

check "refuses a /ship prompt (headless never merges)" 2 \
  "$("$SCRIPT" --cwd "$WORK/project" --prompt '/ship 12' >/dev/null 2>&1; echo $?)"
printf '\n  /ship 12\n' >"$WORK/ship-brief.md"
check "refuses a brief that starts with /ship" 2 \
  "$("$SCRIPT" --cwd "$WORK/project" --brief "$WORK/ship-brief.md" >/dev/null 2>&1; echo $?)"
# /execute ends by merging as the merge rules allow; headless, nobody could answer.
check "refuses an /execute prompt (it can merge)" 2 \
  "$("$SCRIPT" --cwd "$WORK/project" --prompt '/execute --local "fix the typo"' >/dev/null 2>&1; echo $?)"
printf '\n  /execute "fix the typo"\n' >"$WORK/execute-brief.md"
check "refuses a brief that starts with /execute" 2 \
  "$("$SCRIPT" --cwd "$WORK/project" --brief "$WORK/execute-brief.md" >/dev/null 2>&1; echo $?)"

check "the only architech on PATH is the fake" "$WORK/bin/architech" "$(command -v architech)"

# Stopping a run that is still going, as dispatch.md documents: TERM to the group
# named in pgid.txt while the runner is alive. The runner sees Architech die by a
# signal and must grade it INTERRUPTED, not FAILED.
pidfile="$WORK/grandchild-pgid.pid"
FAKE_MODE=hang FAKE_PIDFILE="$pidfile" "$SCRIPT" --cwd "$WORK/project" --prompt x \
  --timeout 600 --run "$WORK/run-pgid" >/dev/null 2>&1 &
runner=$!
for _ in $(seq 50); do [ -s "$pidfile" ] && [ -s "$WORK/run-pgid/pgid.txt" ] && break; sleep 0.2; done
kill -TERM -- -"$(cat "$WORK/run-pgid/pgid.txt" 2>/dev/null || echo 999999)" 2>/dev/null || true
wait "$runner" 2>/dev/null || true
check "TERM to the recorded group: verdict INTERRUPTED" INTERRUPTED "$(cat "$WORK/run-pgid/verdict.txt" 2>/dev/null)"
check "TERM to the recorded group: rc.txt 143" 143 "$(cat "$WORK/run-pgid/rc.txt" 2>/dev/null)"
for which in "$pidfile" "$pidfile.fake"; do
  check "TERM to the recorded group: $(basename "$which") gone" gone \
    "$(kill -0 "$(cat "$which" 2>/dev/null || echo 999999)" 2>/dev/null && echo alive || echo gone)"
done

# A hard kill (SIGKILL) of the runner cannot be trapped: no verdict, and Architech's
# group keeps running. pgid.txt names that group so the caller can stop exactly it.
pidfile="$WORK/grandchild-kill.pid"
FAKE_MODE=hang FAKE_PIDFILE="$pidfile" "$SCRIPT" --cwd "$WORK/project" --prompt x \
  --timeout 600 --run "$WORK/run-kill" >/dev/null 2>&1 &
runner=$!
for _ in $(seq 50); do [ -s "$pidfile" ] && break; sleep 0.2; done
check "pgid.txt names Architech's process group" \
  "$(ps -o pgid= -p "$(cat "$pidfile.fake")" | tr -d ' ')" "$(cat "$WORK/run-kill/pgid.txt" 2>/dev/null)"
kill -KILL "$runner"; wait "$runner" 2>/dev/null || true; sleep 1
check "a hard kill leaves no verdict" none "$([ -e "$WORK/run-kill/verdict.txt" ] && echo written || echo none)"
check "a hard kill leaves Architech running" alive \
  "$(kill -0 "$(cat "$pidfile.fake")" 2>/dev/null && echo alive || echo gone)"
kill -TERM -- -"$(cat "$WORK/run-kill/pgid.txt" 2>/dev/null || echo 999999)" 2>/dev/null || true; sleep 1
for which in "$pidfile" "$pidfile.fake"; do
  check "the documented cleanup stops $(basename "$which")" gone \
    "$(kill -0 "$(cat "$which" 2>/dev/null || echo 999999)" 2>/dev/null && echo alive || echo gone)"
done

# Operate option 3 exactly as documented: the runner inside a detached tmux session
# on a private server with no user config, started from the project directory with
# the skill's absolute script path. The temp HOME carries a hostile ~/.tmux.conf
# (keeps dead panes open); -f /dev/null must keep it out.
if command -v tmux >/dev/null 2>&1; then
  mkdir -p "$WORK/home"; echo 'set -g remain-on-exit on' >"$WORK/home/.tmux.conf"
  sock="unsup-test-$$"
  (cd "$WORK/project" && env -i HOME="$WORK/home" PATH="$PATH" TERM=xterm FAKE_MODE=done \
    tmux -L "$sock" -f /dev/null new-session -d -s run-t \
    "$SCRIPT --cwd $WORK/project --prompt x --run $WORK/run-tmux --timeout 60")
  for _ in $(seq 50); do [ -s "$WORK/run-tmux/verdict.txt" ] && break; sleep 0.2; done
  sleep 1
  check "option 3 from the project dir: verdict DONE" DONE "$(cat "$WORK/run-tmux/verdict.txt" 2>/dev/null)"
  check "option 3: the private server exits by itself" gone \
    "$(env -i HOME="$WORK/home" PATH="$PATH" tmux -L "$sock" has-session 2>/dev/null && echo alive || echo gone)"
  env -i HOME="$WORK/home" PATH="$PATH" tmux -L "$sock" kill-session -t '=run-t' 2>/dev/null || true
else
  echo "skip option 3 (tmux not installed)"
fi

check "rejects a missing --cwd"     2 "$("$SCRIPT" --prompt x >/dev/null 2>&1; echo $?)"
check "rejects a non-numeric cap"   2 "$("$SCRIPT" --cwd "$WORK/project" --prompt x --timeout 1m >/dev/null 2>&1; echo $?)"
check "rejects a zero cap"          2 "$("$SCRIPT" --cwd "$WORK/project" --prompt x --timeout 0 >/dev/null 2>&1; echo $?)"
check "rejects a missing brief"     2 "$("$SCRIPT" --cwd "$WORK/project" --brief "$WORK/nope.md" >/dev/null 2>&1; echo $?)"
check "rejects no prompt at all"    2 "$("$SCRIPT" --cwd "$WORK/project" >/dev/null 2>&1; echo $?)"
check "rejects an unknown argument" 2 "$("$SCRIPT" --cwd "$WORK/project" --prompt x --bogus >/dev/null 2>&1; echo $?)"

echo "$PASS passed, $FAILN failed"
[ "$FAILN" -eq 0 ]
