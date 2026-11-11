# Hand work to Architech from Claude Code or Codex

Decide, brief, run, read the verdict: one pattern for both modes.

## 1. Decide in ten seconds

1. A repo-local edit this agent can do itself? Do it here.
2. Needs Architech's planning, review or parallel agents, in a repository where
   Architech is onboarded? Hand it over.
3. Will it need decisions along the way? **Background session** (section 3).
   Fully briefed? **Headless** (section 2).
4. Needs a merge? Neither mode merges for the user: they run `/ship`
   interactively, or approve the merge in the background session.

## 2. Mode A: headless (`architech -p`)

### What happens to questions

A headless run has nobody to ask, so its ask-the-user tool is not offered at
all. The run decides by itself or stops and says why, and it still exits 0.
Checked on 0.1.46: a headless run that was told to ask a question had no way to,
and ended `BLOCKED`. So the brief carries every answer up front and says
"open a pull request, do not merge".

### The one command

```text
scripts/run-headless.sh --cwd <project> (--brief <file> | --prompt "<text>")
                        [--timeout <seconds>] [--run <dir>]
```

It runs `architech -p` from the project directory with stdin closed and caps
the wall clock (without `timeout`, which macOS lacks). At the cap, or when the
script itself is stopped (TERM, INT, HUP), it stops Architech's whole process
group and still writes a verdict. It refuses a prompt that starts with `/ship`.

A run usually outlasts one shell call (Claude Code stops a call after 2
minutes by default, 10 at most), so start it in the background and poll. In
Claude Code, use the shell tool's background option; elsewhere:

```bash
mkdir -p /abs/run
nohup scripts/run-headless.sh --cwd /abs/path/to/project \
  --brief /abs/run/brief.md --run /abs/run --timeout 1800 >/abs/run/runner.log 2>&1 &
```

Then check every minute or so until `/abs/run/verdict.txt` exists. The run
directory holds:

| File | Holds |
|---|---|
| `out.txt` | Architech's answer |
| `err.txt` | Errors (sign-in, provider, network) |
| `rc.txt` | Exit code (124 = stopped at the cap; 128+n = the script got signal n) |
| `verdict.txt` | `DONE`, `BLOCKED`, `FAILED`, `NO_VERDICT`, `TIMEOUT` or `INTERRUPTED` |

It prints one line, `run=<dir> rc=<code> verdict=<verdict>`, and exits 0 once a
verdict is written: read the verdict, not the script's exit code.

By hand, without the script:

```bash
cd /abs/path/to/project && architech -p "<prompt>" </dev/null >out.txt 2>err.txt
```

plus your own wall-clock cap.

### Non-negotiables

1. **Close stdin.** Print mode waits on an open stdin; an agent's shell keeps
   it open, so the run never returns. Checked on 0.1.46: with stdin open, a run
   that answers in seconds was still waiting after 15 s.
2. **Always `-p`.** A bare `architech` opens the interactive screen and never
   returns.
3. **Cap the wall clock**, and stop the process group, not just the parent.
4. **Sign in first:** `/login` once in an interactive session on that machine.
   Never a key on the command line.
5. **Exit 0 means the turn ended.** Read the verdict.

### Verdicts

| Verdict | Meaning | Next step |
|---|---|---|
| `DONE` | The brief's last line said done | Read the output file the brief named; check its "Done when" |
| `BLOCKED` | It needed a decision it could not ask for | Read `out.txt`, add the answer to the brief, run again |
| `NO_VERDICT` | The turn ended without the brief's last line | Read `out.txt`; usually a missing answer or an unclear brief |
| `FAILED` | It said it failed, or exited non-zero | Read `err.txt` first: sign-in, provider, network |
| `TIMEOUT` | Stopped at the cap; nothing left running | Narrow the task or raise `--timeout` |
| `INTERRUPTED` | The script was stopped (a shell-call limit, Ctrl-C); Architech was stopped too | Start it in the background, as above |

### Long runs and fan-out

- **Claude Code:** one shell call has a time limit. Start the script in the
  background and poll for `verdict.txt` every minute or so.
- **Codex (expected; not yet tested):** the sandbox will likely need to allow
  network access and Architech's own writes outside the workspace; otherwise
  expect permission or network errors that are not Architech faults.
- **Parallel:** one `--run` directory per task. Several headless runs can go at
  once; each one is its own session.

## 3. Mode B: background session in tmux (can ask)

### What happens to questions

Yes, it can ask. The background session is the normal interactive one, so a
question appears in the pane as a menu with numbered options. Checked on 0.1.46
with tmux 3.6a: the question showed in the pane, `Down` then `Enter` picked the
second option, and the session carried on with that answer.

### Commands (tmux is the only extra tool)

Two rules for every tmux command:

- **Its own server:** always `-L unsupervised`. Your sessions then live apart
  from the user's own tmux sessions, and nothing you do can touch theirs.
- **Exact targets:** `-t '=arch-<task>'` for session commands and
  `-t '=arch-<task>:'` (with the colon) for pane commands. A bare
  `-t arch-<task>` also matches a longer name that starts with it, so it can
  type into, or kill, another task's session.

| Step | Command |
|---|---|
| Start | `tmux -L unsupervised new-session -d -s arch-<task> -x 160 -y 50 -c /abs/path/to/project architech` |
| Type a task | `tmux -L unsupervised send-keys -t '=arch-<task>:' -l '<text>'` then `tmux -L unsupervised send-keys -t '=arch-<task>:' Enter` |
| Read | `tmux -L unsupervised capture-pane -p -t '=arch-<task>:' -S -200` |
| Answer a menu | `tmux -L unsupervised send-keys -t '=arch-<task>:' Down` (or `Up`) to move, then the same with `Enter` to pick |
| Is it still there? | `tmux -L unsupervised has-session -t '=arch-<task>'` |
| The user watches or takes over | `tmux -L unsupervised attach -t '=arch-<task>'` (detach: `Ctrl-b d`) |
| Stop | type `/exit` into the pane (send it with `-l`, then `Enter`) |
| Stop, if `/exit` gets no answer | see below |

If the session does not respond to `/exit`, stop Architech itself, not just
the tmux session. `kill-session` alone can leave Architech running with no
screen: checked on 0.1.46, it survived the session's hangup. Stop the pane's
process group instead; the pane, and the session, then close on their own:

```bash
pid=$(tmux -L unsupervised display-message -p -t '=arch-<task>:' '#{pane_pid}')
kill -TERM -- "-$pid"
tmux -L unsupervised has-session -t '=arch-<task>' 2>/dev/null &&
  tmux -L unsupervised kill-session -t '=arch-<task>'
```

Give each task its own session name. Stop only the session you started.
**Never run `tmux kill-server`**, with or without `-L`: it ends every session
on that server, including other tasks'.

### Who answers what

| Question | Who answers |
|---|---|
| Plan approval, merge, anything destructive | **The user.** Relay it word for word with the options; type their answer |
| A clarifying question the brief already answers | You. Then tell the user what you answered |
| Unsure which kind it is | Relay it |

### Reading the pane

Poll every 20-60 seconds. Look for three states rather than exact characters,
which change between releases:

- **Working:** new output keeps appearing.
- **Asking:** a question with numbered options and a hint line about
  `Enter` to select.
- **Idle:** the input line is empty and the output has stopped; the task is
  done or waiting for you.

### Trade-offs

- Plus: questions work; the user can attach; long work keeps its context.
- Minus: you read a screen, not structured output, and the layout can change
  between releases.
- Minus: needs tmux (`brew install tmux`, `apt install tmux`). tmux may print
  an "extended-keys is off" warning; plain `Enter` still works.
- Minus: polling costs tokens. Prefer Mode A when the task is fully briefed.

## 4. The brief

Start from [the brief template](../assets/brief-template.md). It holds:

- the outcome, not the activity;
- the project's absolute path and every input as an absolute path;
- constraints, including "open a pull request, do not merge";
- the output file;
- a last line that is exactly one `VERDICT:` line.

## 5. Smoke test (seconds, after `/login`)

Short enough to run in the foreground: the cap stays well under one shell call.

```bash
scripts/run-headless.sh --cwd /abs/path/to/project \
  --prompt 'Reply with exactly two lines: PONG, then VERDICT: DONE' --timeout 60
# -> ... verdict=DONE
```
