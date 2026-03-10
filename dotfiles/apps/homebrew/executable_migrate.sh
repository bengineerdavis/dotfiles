#!/usr/bin/env bash

#!/usr/bin/env bash

# Define the new app directory
APP_DIR="$HOME/Applications"
mkdir -p "$APP_DIR"

# Get current casks
casks=$(brew list --cask)

for cask in $casks; do
    echo "==> Processing $cask..."
    # --force ignores the "already exists" error
    # --zap removes the metadata/Caskroom folder causing the block
    brew uninstall --cask --force --zap "$cask"
    
    # Reinstall to the new directory
    brew install --cask "$cask" --appdir="$APP_DIR"
done

# Cleanup orphaned dependencies and cache
brew autoremove
