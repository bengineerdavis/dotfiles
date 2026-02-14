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

chezmoi init "git@github.com:$GITHUB_USERNAME/dotfiles.git"
chezmoi apply
brew bundle --file="$HOME/dotfiles/bootstrap/Brewfile"