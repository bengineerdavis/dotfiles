### Added

- loreai topic (`apps/loreai`): the Lore.AI persistent-memory gateway for
  coding agents. The `lore` binary installs checksum-verified from
  BYK/loreai releases (the `apps/ori` pattern — the topic owns its
  upgrades), first-install prompts for telemetry and worker-model
  inference are saved per machine to `~/.config/loreai/env.zsh`, and each
  detected coding agent is wired up as an extension: `lore setup` for
  claude-code/codex/pi/hermes, and a chezmoi-included
  `@loreai/opencode` plugin fragment for opencode, whose config chezmoi
  owns. Background workers default to OpenRouter (`z-ai/glm-5.3-flash`)
  where a key is available, with reviewed fallbacks and a 32B-class local
  tier recorded in the machine env file. `--tags remove` undoes each
  agent's setup and removes the binary while preserving the memory
  database.
