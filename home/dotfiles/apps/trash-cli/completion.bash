#!/usr/bin/env bash

bash_completion_dir="$HOME/.local/share/bash-completion/completions"
fpath=("$bash_completion_dir" $fpath)
cmds=(trash-empty trash-list trash-restore trash-put trash)

mkdir -pv $bash_completion_dir

for cmd in "${cmds[@]}"; do
  command -v "$cmd" >/dev/null 2>&1 || continue

  # bash
  
  if [[ -d "$bash_completion_dir" ]]; then

    echo "(Re-)generating bash completion for $cmd..."
    bash_target="$bash_completion_dir/$cmd"
    if [[ ! -f "$bash_target" ]]; then
      "$cmd" --print-completion bash 2>/dev/null \
        | sudo tee "$bash_target" >/dev/null
        echo "Generated bash completion for $cmd at $bash_target"
    fi

  fi

done

