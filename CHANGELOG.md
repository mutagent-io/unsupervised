# Changelog

## [0.1.4] - 2026-11-25

Checked against Architech 0.1.67 (`metadata.architech_checked`).

### Changed
- Re-checked on Architech 0.1.67, the current release: the four autonomy
  presets and their gates, the retired `factory.yaml` forms, `factory init`
  (still needs `--project` and an existing folder), the `update --check`
  output, and the headless runner (smoke test, a question it can't ask).
- The repository-issues board (`ref: { owner, repo }`) for personal accounts:
  Cloud accepts it, but `architech factory validate` and `push` still refuse
  it on 0.1.67, despite its release notes. The skill now says so, instead of
  saying 0.1.67 fixes it; the failure table names the workaround (an
  organisation's Project) until a CLI fix ships.

## [0.1.3] - 2026-11-25

Checked against Architech 0.1.66 (`metadata.architech_checked`).

### Added
- `check_skill.py` checks the factory language (the four presets, no retired
  forms or label names), the Codex `short_description` length and the brief
  template's `VERDICT:` lines.

### Fixed
- **When a person is asked.** The skill, README, FAQ and workflows page said
  every merge waits for the user at every autonomy level. They now say it per
  `policy.autonomy` preset: `calibrating` (the default) waits on every plan
  and every merge; `approve-merges` on every merge and on a spec-sized plan;
  `approve-plans` on every plan and merges by itself once the review says
  APPROVE or WATCH and CI is green; `unsupervised` only on a spec-sized plan.
  A merge that runs by itself still asks on an exception. A
  repository with no factory file asks before every merge. Review sends work
  back at most 2 rounds by default.
- `references/factory.md` speaks the 0.1.66 `factory.yaml` language: the four
  `policy.autonomy` presets, `policy.merge.approve`, `policy.plan` (`approve`,
  `subItems`), `policy.code-review.maxLoops`, `repos[].ci`, the `fastLane`
  label, and the approval label `merge:ready`. The retired forms it taught
  (`policy.merge.preset`, autonomy `standard`/`autonomous`, a top-level
  `plan.subItems`) are refused by 0.1.66's `validate`.
- Boards: an organisation's GitHub Project, or, on a personal account, the
  repository's issues (`ref: { owner, repo }`; Cloud can't bind a personal
  Project, `BOARD_PROJECT_USER_OWNED`). The CLI validates the repository-issues
  form from Architech 0.1.67, not yet released. An issue must be on the board,
  carry the pickup label and sit outside Triage; assigning it to the Factory
  is a default trigger too. `push` links the repositories and binds the board.
- `architech factory init` needs `--project` (or a hand-edited `ref`), and the
  folder must exist first.
- Onboarding always writes a `mode: local` factory file and the `CLAUDE.md`
  pointer, even with no board. A board is added later with
  `architech-onboard tracking --org <owner> --project <number>`, labels with
  `architech-onboard labels --apply`. `/workflows <name>` shows a workflow; it
  doesn't run it.
- The installed Claude Code plugin lives in
  `~/.claude/plugins/cache/<marketplace>/unsupervised/<version>/`.
- `install.md`: the installer's root, `PATH` collision, rate-limit, network and
  disk-space refusals, the 0.1.66 `update --check` output, and
  `uninstall --reset`.
- `dispatch.md`: the runner exits 128+n when it is stopped by a signal;
  `kill-session` leaving Architech running was seen on 0.1.49, not on 0.1.66.
- The brief template's `VERDICT:` lines are flush left: the runner matches the
  reply's last line exactly.
- FAQ: the troubleshooting cross-reference points at SKILL.md section 7;
  links to the lifecycle-commands and Software Factory docs.

### Changed
- Plugin, marketplace and Codex descriptions mention the Software Factory,
  Early Access and any harness; Codex's `short_description` fits its 64-char
  limit and the Codex metadata names the icon.
- The trigger eval no longer says "unsupervised while I review the plan".
- README: a Quick start where every line was run, and a note that the plugin
  is not in Anthropic's plugin directory (both on `main` after 0.1.2).

## [0.1.2] - 2026-11-16

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
