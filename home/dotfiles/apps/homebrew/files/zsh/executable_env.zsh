### Brew config

# detect bat cli before setting env var
if command -v bat &> /dev/null; then
  export HOMEBREW_BAT=on
else
  export HOMEBREW_BAT=off
fi

# Add new concurrency env for v4.5.0+
export HOMEBREW_DOWNLOAD_CONCURRENCY=auto
# Enables bat for brew cat command output (syntax highlighting and paging)
export HOMEBREW_NO_ANALYTICS=1
export HOMEBREW_CLEANUP_PERIODIC_FULL_DAYS=7
# If set, always assume --debug when running commands.
# export HOMEBREW_DEBUG=1
# Run brew update once every $HOMEBREW_AUTO_UPDATE_SECS seconds before some commands, e.g. brew install, brew upgrade or brew tap. Alternatively, disable auto-update entirely with $HOMEBREW_NO_AUTO_UPDATE.
# Default: 86400 (24 hours), 3600 (1 hour) if a developer command has been run or 300 (5 minutes) if $HOMEBREW_NO_INSTALL_FROM_API is set.
export HOMEBREW_AUTO_UPDATE_HOURS=24
export HOMEBREW_AUTO_UPDATE_SECS=$((60*60*${HOMEBREW_AUTO_UPDATE_HOURS:-24}))

# system-specific options and environment variables
if [ "$(uname -s)" = "Darwin" ]; then
  # macOS-only: e.g. Homebrew is at /opt/homebrew (Apple Silicon) or /usr/local (Intel)
  export HOMEBREW_CASK_OPTS="--appdir=~/Applications"
elif [ "$(uname -s)" = "Linux" ]; then
  # Linux-only: linuxbrew doesn't support casks
  :
fi