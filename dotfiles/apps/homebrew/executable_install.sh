#!/bin/sh
#
# Homebrew
#
# This installs some of the common dependencies needed (or at least desired)
# using Homebrew.

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

# Link keg-only formulas that we want in PATH
brew list | grep 'postgresql@' | xargs -I {} brew link {} --force 2>/dev/null

exit 0