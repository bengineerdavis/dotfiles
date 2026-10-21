# shellcheck shell=bash
# loreai — process-level environment for Lore.AI.
# Sourced by ~/.zshrc via the canonical glob $ZSH/apps/*/files/zsh/*.zsh.

# The topic owns upgrades (checksum-compared fetch, --tags upgrade), so the
# CLI's own "new version available" check would only nag about a channel it
# cannot use. https://withlore.ai/docs/environment/
export LORE_NO_UPDATE_CHECK=1

# Per-machine choices (telemetry, worker-model inference), written by the
# topic's first-install prompts. Not managed by chezmoi — each machine
# answers for itself.
# shellcheck source=/dev/null
[[ -r "$HOME/.config/loreai/env.zsh" ]] && source "$HOME/.config/loreai/env.zsh"
