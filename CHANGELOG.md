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
- `run-headless.sh` stops Architech and writes `INTERRUPTED` when it is itself
  stopped, refuses a `/ship` prompt, and is meant to run in the background.
- Background sessions run on their own tmux server (`-L unsupervised`) with
  exact targets.
- Checked against Architech 0.1.46 on macOS: headless runs cannot ask and end
  `BLOCKED` when they need a decision; a background tmux session shows a
  question as a menu that the calling agent can answer. Linux and the Codex
  sandbox are expected to work, not yet tested.
