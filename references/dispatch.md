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

```bash
scripts/run-headless.sh --cwd /abs/path/to/project \
  (--brief /abs/run/brief.md | --prompt "<text>") [--timeout 900] [--run /abs/run-dir]
```

It runs `architech -p` from the project directory with stdin closed, caps the
wall clock (without `timeout`, which macOS lacks), stops the whole process
group at the cap, and writes into the run directory:

| File | Holds |
|---|---|
| `out.txt` | Architech's answer |
| `err.txt` | Errors (sign-in, provider, network) |
| `rc.txt` | Exit code (124 = stopped at the cap) |
| `verdict.txt` | `DONE`, `BLOCKED`, `FAILED`, `NO_VERDICT` or `TIMEOUT` |

It prints one line: `run=<dir> rc=<code> verdict=<verdict>`.

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

### Long runs and fan-out

- **Claude Code:** one shell call has a time limit. Start the script in the
  background and poll for `verdict.txt` every minute or so.
- **Codex:** the sandbox must allow network access and Architech's own writes
  outside the workspace; otherwise expect permission or network errors that are
  not Architech faults.
- **Parallel:** one `--run` directory per task. Several headless runs can go at
  once; each one is its own session.

## 3. Mode B: background session in tmux (can ask)

### What happens to questions

Yes, it can ask. The background session is the normal interactive one, so a
question appears in the pane as a menu with numbered options. Checked on 0.1.46
with tmux 3.6a: the question showed in the pane, `Down` then `Enter` picked the
second option, and the session carried on with that answer.

### Commands (tmux is the only extra tool)

| Step | Command |
|---|---|
| Start | `tmux new-session -d -s arch-<task> -x 160 -y 50 -c /abs/path/to/project architech` |
| Type a task | `tmux send-keys -t arch-<task> -l '<text>'` then `tmux send-keys -t arch-<task> Enter` |
| Read | `tmux capture-pane -p -t arch-<task> -S -200` |
| Answer a menu | `tmux send-keys -t arch-<task> Down` (or `Up`) to move, then `... Enter` to pick |
| The user watches or takes over | `tmux attach -t arch-<task>` (detach: `Ctrl-b d`) |
| Stop | type `/exit` into the pane, or `tmux kill-session -t arch-<task>` |

Stop only the session you started. **Never run `tmux kill-server`**: it ends
every tmux session the user has, not just yours. If you want your sessions
fully separate from the user's, give every command the same private socket,
for example `tmux -L arch new-session ...`, `tmux -L arch capture-pane ...`;
the user then attaches with `tmux -L arch attach -t arch-<task>`.

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

## 5. Smoke test (30 seconds, after `/login`)

```bash
scripts/run-headless.sh --cwd /abs/path/to/project \
  --prompt 'Reply with exactly two lines: PONG, then VERDICT: DONE' --timeout 120
# -> ... verdict=DONE
```
