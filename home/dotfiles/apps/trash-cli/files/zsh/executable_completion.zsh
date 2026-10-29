#!/usr/bin/env bash

zsh_completion_dir="$HOME/.local/share/zsh/site-functions"
fpath=("$zsh_completion_dir" $fpath)
cmds=(trash-empty trash-list trash-restore trash-put trash)

for cmd in "${cmds[@]}"; do
  command -v "$cmd" >/dev/null 2>&1 || continue

  # zsh completion
  if [[ -d "$zsh_completion_dir" ]]; then

    zsh_target="$zsh_completion_dir/_$cmd"
    if [[ ! -f "$zsh_target" ]]; then
      echo "(Re-)generating zsh completion for $cmd..."
      "$cmd" --print-completion zsh 2>/dev/null \
        | sudo tee "$zsh_target" >/dev/null
        echo "Generated zsh completion for $cmd at $zsh_target"
    fi

  fi

done

