# Rancher Desktop installs the docker / nerdctl / kubectl CLIs and the
# `docker compose` v2 plugin into ~/.rd/bin. Put it on PATH so the engine is
# reachable in interactive shells.
#
# This replaces the unmanaged "### MANAGED BY RANCHER DESKTOP" block that
# Rancher writes into ~/.zshrc — the PATH edit is owned by this topic per
# docs/CONVENTIONS.md. Self-guarding: if the topic is removed (cask gone),
# ~/.rd/bin no longer exists and this is a no-op, so no remove.yaml teardown
# is needed.
[[ -d "$HOME/.rd/bin" ]] && export PATH="$HOME/.rd/bin:$PATH"
