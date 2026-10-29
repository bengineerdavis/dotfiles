# Ollama shell environment.
#
# Sourced by ~/.zshrc via the canonical glob `$ZSH/apps/*/files/zsh/*.zsh`.
# (A copy at apps/ollama/env.zsh is the LEGACY flat layout and is NOT sourced —
# don't put anything there expecting it to load.)
#
# ── What this can and cannot configure ───────────────────────────────────────
# Shell exports only reach processes started FROM a shell: CLI clients, and a
# shell-launched `ollama serve`. The macOS Ollama.app starts its own server and
# never reads your shell — verified by inspecting the running process, which
# carried settings from the app's own database rather than from here.
#
# So server tuning is published twice, from ONE definition (`ollama_server_env`
# in apps/ollama/defaults/main.yaml):
#   here            -> `ollama-role serverenv`, for shell-launched servers
#   launchctl setenv -> done by ansible, for the GUI app (needs an app restart)
# Nothing is restated literally in this file, so the two cannot drift.

if command -v ollama-role >/dev/null 2>&1; then
  # Server tuning: flash attention + q8_0 KV cache, cloud disabled, context and
  # keep-alive sized for a 36GB machine. See defaults/main.yaml for the
  # measurements behind each value.
  if [[ "$OSTYPE" == darwin* ]]; then
    eval "$(ollama-role serverenv 2>/dev/null)"
  fi

  # Role -> model bindings, so scripts name a task instead of hardcoding a tag:
  #   $OLLAMA_ROLE_CODE, $OLLAMA_ROLE_AUDIO, $OLLAMA_ROLE_ESCALATE, …
  # Resolved at shell start and capability-checked against `ollama show`, so a
  # model that lacks the capability (every gemma4 MLX build lacks audio) drops
  # out rather than silently resolving to something that cannot do the job.
  eval "$(ollama-role env 2>/dev/null)"
fi
