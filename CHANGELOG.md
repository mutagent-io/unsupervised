# Changelog

## [0.1.0] - unreleased

### Added
- First release: install Architech with the public installer, onboard a
  repository, choose a flow (Full-Loop or Fast Mode), and hand work to
  Architech from Claude Code or Codex, headless (`scripts/run-headless.sh`) or
  in a background tmux session that can ask questions.
- Checked against Architech 0.1.46: headless runs cannot ask and end
  `BLOCKED` when they need a decision; a background tmux session shows a
  question as a menu that the calling agent can answer.
