# zsh/fpath.zsh

if [ -d "$HOME/.zsh_completions" ]; then
  fpath=("$HOME/.zsh_completions" $fpath)
fi