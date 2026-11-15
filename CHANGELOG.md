# Changelog

## [0.1.0] - unreleased

### Added
- Harness-neutral: works from any agent harness that can read files and run
  shell commands, in three phases (start, setup, operate), with capability
  checks, a short per-host table, and fallbacks without tmux or without a
  shell. `AGENTS.md` and a README "For agents" section point other harnesses
  to the same steps.
- First release: install Architech with the public installer, onboard a
  repository, choose a flow (Full-Loop or Fast Mode), and hand work to
  Architech from Claude Code or Codex, headless (`scripts/run-headless.sh`) or
  in a background tmux session that can ask questions.
- Background and detached runs start a private tmux server with `-f /dev/null`,
  so none of the user's tmux config (session restore or autosave plugins) runs
  in it. The runner is always called by its absolute path in the skill folder.
- A run stopped from outside (its process group got a signal) is graded
  `INTERRUPTED`, not `FAILED`; dispatch.md shows how to stop a run that is
  still going by its recorded group.
- Where to find the skill's folder when a harness shows it only by name or URI,
  without searching the home folder or re-typing the runner.
- Write or commit questions, and a choice of how to land a change, are relayed
  to the user like plan and merge questions.
- `run-headless.sh` writes `pgid.txt`, so a run whose runner was killed outright
  (no verdict, runner gone) can be stopped exactly; the docs cover that outcome.
- `run-headless.sh` stops Architech and writes `INTERRUPTED` when it is itself
  stopped, refuses a `/ship` prompt, and is meant to run in the background.
- Background sessions run on their own tmux server (`-L unsupervised`) with
  exact targets.
- Checked against Architech 0.1.49. On macOS: headless runs cannot ask and end
  `BLOCKED` when they need a decision; a background tmux session shows a
  question as a menu the calling agent can answer; journeys in Claude Code and
  in Codex ended with a headless run that pushed an unmerged branch. Codex's
  default sandbox asks you to approve each `tmux -L unsupervised` call,
  `architech update --check` and `pgrep`, and in one test it answered two
  approval questions itself, which the relay rules above now forbid. On Linux:
  a clean install, `doctor --strict` and the offline test suites passed on
  Ubuntu 24.04 arm64, with no model run yet. Linux x64 and other harnesses are
  expected to work, not yet tested.
