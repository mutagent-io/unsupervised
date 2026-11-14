# Contributing

Thanks for helping. This repository is one skill, and **the repository root is
the skill folder**: whatever is here is copied to every user who installs it.
Keep it small, and treat every file as public.

## Rules

- **Public content only.** No machine paths, private repository names,
  internal tool names, environment variables, keys or tokens.
- **Every command the skill names must be public:** on the Architech boot
  screen or on https://docs.mutagent.io/architech. When the product and the
  skill disagree, the product wins; fix the skill.
- **No `CLAUDE.md` in this repository.** The root is the installed skill
  folder, and a `CLAUDE.md` here could load into users' sessions. Maintainer
  notes belong in this file.
- **`AGENTS.md` stays a pointer.** It sends harnesses that don't load skills
  natively to `SKILL.md`, and says to ignore it otherwise, so it is harmless if
  a harness loads it into an unrelated session. Never copy steps into it.
- **Harness-neutral.** Host names (Claude Code, Codex, ...) and host tool
  names appear only in SKILL.md section 1's per-host table. Everywhere else,
  describe the capability ("if your harness can run a command in the
  background..."). `check_skill.py` enforces this.
- **Operate safely from anywhere.** Every `tmux ... new-session` in the docs
  starts its private server with `-f /dev/null`, and every runner call is
  `<skill-dir>/scripts/run-headless.sh`. `check_skill.py` enforces both.
- **No `allowed-tools` in `SKILL.md`.** A public skill does not pre-approve its
  own shell commands.
- Keep `SKILL.md` under 500 lines and the `description` under 1024 characters,
  starting with "Architech". References stay one level deep.

## Layout

| Path | What to edit |
|---|---|
| `SKILL.md` | The skill: what a harness needs, rules, start / setup / operate, commands |
| `AGENTS.md` | A pointer to `SKILL.md` for harnesses that don't load skills |
| `references/*.md` | One page per user journey |
| `assets/brief-template.md` | The headless hand-over brief |
| `scripts/run-headless.sh` | The headless runner (bash only) |
| `evals/triggers.json` | Prompts that should and should not load the skill |
| `.claude-plugin/` | Plugin and marketplace manifests |
| `.github/` | CI and the check scripts |

## Run the checks

CI runs all of these on every pull request. Run them locally first:

```bash
python3 .github/scripts/check_skill.py        # structure, limits, versions, icon, trigger list
python3 .github/scripts/sanitize.py --check   # no machine paths, personal emails or secrets
python3 .github/scripts/sanitize.py --check --git   # the same, in commit authors and messages
bash .github/scripts/test-sanitize.sh         # the sanitizer's own tests
bash .github/scripts/test-run-headless.sh     # the runner, against a fake architech
bash .github/scripts/test-build-release.sh    # the release tarball and notes, dry run
bash .github/scripts/test-release-plan.sh     # when a release happens, for every merge shape
shellcheck scripts/*.sh .github/scripts/*.sh
claude plugin validate .                      # Claude Code manifests
skills-ref validate "$PWD"                    # Agent Skills spec; needs a checkout folder named `unsupervised`
```

`skills-ref` installs with
`pip install "git+https://github.com/agentskills/agentskills.git@38a2ff82958afee88dadf4831509e6f7e9d8ef4e#subdirectory=skills-ref"`.
It requires the folder name to match the skill name, so validate from a clone
named `unsupervised`, and pass the path (`.` reads as an empty name).

When you change the description or the trigger list, also run the trigger eval
in Claude Code (one short session per prompt, using your own sign-in):

```bash
python3 .github/scripts/trigger_eval.py
```

It passes when at least 9 in 10 `should_trigger` prompts load the skill and at
most 1 in 10 near misses do.

## Versions and releases

Bump these together, in one pull request:

1. `metadata.skill_version` in `SKILL.md`
2. `version` in `.claude-plugin/plugin.json`
3. the plugin's `version` in `.claude-plugin/marketplace.json`
4. a new top entry in `CHANGELOG.md`

`check_skill.py` fails if they differ. On every push to `main`, the Release
workflow checks whether `v<version>` is tagged yet; if not, it tags it and
publishes the release with the skill tarball in the same job (a tag pushed by a
workflow does not start other workflows). Any way of reaching `main` works:
direct push, squash, merge commit or rebase merge. To publish or re-upload
an existing tag, run the Release workflow by hand with that tag.

When you re-check the skill against a new Architech release, update
`metadata.architech_checked`.
