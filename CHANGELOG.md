# Changelog

## [0.1.2] - unreleased

### Added
- **Delegate, never implement.** The agent operating Architech hands every
  build, fix or feature request in a repository set up with Architech to
  Architech or its factory, and never edits the project's code itself. It
  writes the brief, relays questions, follows the run and reports. It changes
  code only when the user explicitly asks it to, and then says it isn't using
  Architech. This is the first instruction of SKILL.md's operate phase, of
  the README's "For agents" section and of dispatch.md's decision list, and
  workflows.md says it too. In a repository that isn't set up, the skill
  steps aside in one line and offers onboarding instead of taking the task.
- Local first, then the cloud question: after onboarding sets up the local
  factory, the agent asks whether to move it to Mutagent Cloud, explains what
  that means, and never moves it without a yes. Once the cloud factory is
  set up, it asks per job whether to run it on the cloud or locally.
- Trigger cases: build requests that name Architech or the factory, and plain
  code requests outside a set-up repository as near misses.
- `check_skill.py` guards the delegation wording, the local-first order and
  the manual's section order.

### Changed
- `references/factory.md` is now the Software Factory operator's manual, in
  the order you use it: set up the local factory, run work locally, move to
  the cloud (ask first), run work on the cloud, follow runs, failures, safety.
- The description covers build requests in a repository already set up with
  Architech.

## [0.1.1] - 2026-11-15

### Added
- Software Factory: `references/factory.md` covers choosing local or Cloud mode
  (the user's own session vs Mutagent Cloud's sandboxes), linking a GitHub
  Project board and repositories during onboarding, what `factory.yaml` holds
  (board, repositories, label roles, merge preset, autonomy), running work
  locally (`/sync`, `/spec` -> `/publish` -> `/dispatch`, `/execute`) and on
  Cloud (`architech factory` push, enable, runs), following runs, relaying
  gates and escalations, common failures, and the safety rules: the agent
  never adds or removes a person's label, never approves a gate, never merges.
  Its CLI is `architech factory`, not `mutagent factory` (the Agent Factory).
  SKILL.md points to it, and the description and trigger cases cover it.
- The description rules out the Agent Factory (`mutagent factory`), so a
  request about it no longer loads this skill.

### Changed
- README rewritten around the Software Factory: what you get, how it runs
  locally or on Mutagent Cloud, the install lines, and what stays yours.

### Fixed
- `/execute` is described as it works: it plans, builds, has the pull request
  reviewed, then merges as your merge rules allow, so in Fast Mode the merge is
  what you approve. Agents tell the user before they start it and relay its
  merge question, and `scripts/run-headless.sh` refuses an `/execute` prompt
  as it refuses `/ship`.
- The label table: `merge:hold` stops work whoever adds it. `runs approve
  --request-changes` (in `--help`, not yet in the docs) is listed with the
  other user-only approval commands. The README says onboarding commits two
  files.
- `plugin.json` declares `"skills": ["./"]`, which older Claude Code releases
  accept (a bare `"."` was refused).
- The Release workflow publishes only after Validate passed on the same
  commit; a manual release needs a passing Validate run on the tag's commit.
- CI pins the Claude Code version used for `claude plugin validate`.

## [0.1.0] - 2026-11-15

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
