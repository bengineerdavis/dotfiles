#!/usr/bin/env bash

# Use this script once on a new machine or VM to set up my personal machine environment

### mac machines ###
GITHUB_USERNAME=bengineerdavis

# make sure all install commands have executable priviledges 
chmod -v +x **/*install*

xcode-select --install || echo "XCode already installed"

# Install Homebrew if necessary
if which -s brew; then
    echo 'Homebrew is already installed'
else
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    (
        echo
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"'
    ) >>$HOME/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# ── Bootstrap dependency chain for ansible ───────────────────────────────────
# ansible is itself a bootstrap tool (install.sh runs the playbook through it),
# so its whole chain must resolve HERE, in order:
#     uv (system) → mise → mise synced to that uv → mise install → ansible
#
# 1) uv FIRST, at the system level (uv ships uvx). It only needs curl, so it
#    precedes mise. Kept OUT of mise on purpose: mise's pipx backend
#    (pipx.uvx = true) auto-discovers uv/uvx on PATH, so `mise upgrade` never
#    churns the uvx that backs ansible (which used to self-upgrade mid-run).
if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
# uv installs into ~/.local/bin; put it on PATH so mise can discover it below.
export PATH="$HOME/.local/bin:$PATH"

chezmoi init "git@github.com:$GITHUB_USERNAME/dotfiles.git"
chezmoi apply

# 2) mise (and the rest) via brew.
brew bundle --file="$HOME/dotfiles/bootstrap/Brewfile"

# 3) Sync mise to the existing system uv, then materialize tools. mise's pipx
#    backend discovers uv/uvx purely via PATH (no uv tool in mise config), so
#    this builds pipx:ansible with the system uvx — making ansible available
#    before install.sh runs the playbook. Idempotent; re-run by the mise topic.
command -v uv >/dev/null 2>&1 || { echo "ERROR: system uv not on PATH; mise cannot back its uvx" >&2; exit 1; }
mise install --yes