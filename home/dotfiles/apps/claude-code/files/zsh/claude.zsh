# shellcheck shell=bash
# shellcheck source=/dev/null

# Keep direct Claude OAuth separate from the Lore gateway profile.
# ~/.claude-direct owns the normal login, settings and session history;
# ~/.claude remains the Lore profile written by `lore setup claude-code`.
# API keys belong to their provider's profile, never to every Claude process.
# An explicitly exported CLAUDE_CONFIG_DIR wins for one-off/CI use.

typeset -g CLAUDE_DIRECT_CONFIG_DIR="$HOME/.claude-direct"
export CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$CLAUDE_DIRECT_CONFIG_DIR}"

claude() {
  # This also reaches Skillet's direct subprocess through the exported profile.
  # Only the default direct profile strips inherited provider credentials;
  # an explicit custom profile keeps the caller's provider selection intact.
  if [[ "$CLAUDE_CONFIG_DIR" == "$CLAUDE_DIRECT_CONFIG_DIR" ]]; then
    unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN ANTHROPIC_BASE_URL
    unset CLAUDE_CODE_OAUTH_TOKEN
  fi
  command claude "$@"
}

claude-lore() {
  # This wrapper selects the legacy gateway profile; it does not change the
  # gateway route or replace its credential with the direct OAuth login.
  export CLAUDE_CONFIG_DIR="$HOME/.claude"
  # A previous direct wrapper can have cleared these in the same shell.
  # Reload only that invocation's secrets; no secret is persisted by this file.
  [[ -r "$HOME/.localrc" ]] && source "$HOME/.localrc"
  export ANTHROPIC_BASE_URL="http://127.0.0.1:3207"
  command claude "$@"
}
