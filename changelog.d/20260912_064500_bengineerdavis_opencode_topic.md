**Added**

- opencode topic (`apps/opencode`): installs the opencode binary from the
  pinned anomalyco/tap on macOS and Linux, and declares the machine's
  cross-agent skill set (five skills, installed user-global via dotagents).
  Skills auto-load in opencode, claude and cursor from `~/.agents/skills`;
  `--tags remove` uninstalls the binary and keeps the shared skills unless
  `opencode_remove_skills` is flipped.
- chezmoi now manages `~/.config/opencode/opencode.jsonc`: sessions never
  auto-share, one hosted default model with a local small model, and a
  conservative permission baseline (git allowed, everything else asks).
  Provider tokens and session history stay machine-local, as before.
