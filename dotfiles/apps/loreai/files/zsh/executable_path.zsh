# shellcheck shell=bash
# loreai — the `lore` binary installs to ~/.local/bin (LORE_INSTALL_DIR's
# default). The hosted installer would append a marked PATH block to the
# shell profile; this topic owns that concern here instead
# (docs/TOPICS.md § shell wiring). Self-guarding: if the topic is removed
# the directory's absence makes this a no-op, so remove.yaml has no PATH
# teardown. ~/.local/bin is also on PATH via dot_zshrc on this fleet — this
# fragment keeps the topic self-contained for a machine where it is not.
[[ -d "$HOME/.local/bin" ]] && export PATH="$HOME/.local/bin:$PATH"
