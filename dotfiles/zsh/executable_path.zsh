# Add user bin directory to PATH
# ~/.local/bin holds the system uv/uvx (installed by bootstrap.sh via the astral
# installer, intentionally NOT mise-managed). The whole toolchain — the
# `ollama-models` uv single-file script, and mise's pipx backend that builds
# ansible with the system uvx — assumes uv is discoverable on PATH. Persist it
# here so it survives past the bootstrap session (bootstrap.sh only exports it
# transiently), which also lets ansible's `command -v uv` sanity check resolve.
export PATH="$HOME/bin:$HOME/.local/bin:$PATH"