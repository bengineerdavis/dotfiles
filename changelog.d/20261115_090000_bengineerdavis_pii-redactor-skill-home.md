### Fixed

- The opencode config template used `{{ .home }}`, which is not chezmoi data,
  so the template could not render and `chezmoi status` failed for the whole
  repository. It now uses `.chezmoi.homeDir`.
- The suite baseline gate matched node IDs with `\S+`, truncating parametrised
  IDs that contain spaces, so a baselined failure could never match its own
  entry and read as unexpected forever. It now splits on pytest's ` - `
  separator.
- `pii-redactor` let the model's chain-of-thought reach stderr, quoting the
  values it was removing. It now passes `llm -R`.

### Changed

- `pii-redactor`'s implementation and test suite moved to the `pii-redaction`
  skill in `ai-prompt-library`, because the skill specifies the tool. This repo
  keeps a thin wrapper that resolves the skill at run time, so `pii-redactor`
  stays callable from a shell and `~/bin` keeps working.
- The wrapper now reports a bad `PII_REDACTOR_SKILL_SCRIPT` override with the
  actionable message it already gave for a missing skill.
- Two load-bearing `.lore.md` rules are baselined as known failures until Lore's
  re-distillation restores them (DOT-305). Both still describe live behaviour.
