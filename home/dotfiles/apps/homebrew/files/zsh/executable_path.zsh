# see https://github.com/orgs/Homebrew/discussions/2560#discussioncomment-10429972 for why this is needed
if [ -z "$HOMEBREW_PREFIX" ]; then
  case "$(uname -s)" in
    Linux)
      for __brew in "/home/linuxbrew/.linuxbrew/bin/brew" "$HOME/.linuxbrew/bin/brew"; do
        [ -x "$__brew" ] && {
          eval "$("$__brew" shellenv | grep -v '^export PATH=')"
          export PATH="$PATH:${HOMEBREW_PREFIX}/bin:${HOMEBREW_PREFIX}/sbin"
        } && break
      done
      unset __brew
      ;;
    Darwin)
      for __brew in "/opt/homebrew/bin/brew" "/usr/local/bin/brew"; do
        [ -x "$__brew" ] && {
          eval "$("$__brew" shellenv)"
          export PATH="/opt/homebrew/bin:$PATH"
        } && break
      done
      unset __brew
      ;;
  esac
fi