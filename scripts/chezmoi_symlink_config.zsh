# chezmoi_symlink_config
#
# Makes chezmoi manage a symlink like:
#   ~/.config/<app>/<file> → ~/.local/share/chezmoi/dotfiles/apps/<app>/files/<file>
#
# Usage:
#   chezmoi_symlink_config <app> <file>
#
chezmoi_symlink_config() {
  local app="${1:-}"
  local file="${2:-}"
  local chezmoi_src_dir

  if [[ -z "$app" || -z "$file" ]]; then
    echo >&2 "Usage: chezmoi_symlink_config <app> <file>"
    return 1
  fi

  chezmoi_src_dir="$(chezmoi cd && pwd)"
  if [[ $? -ne 0 ]]; then
    echo >&2 "Error: chezmoi cd failed"
    return 1
  fi

  local chezmoi_app_dir="dot_config/${app}"
  local chezmoi_link_file="${chezmoi_app_dir}/symlink_${file}.tmpl"
  local chezmoi_src_file="dotfiles/apps/${app}/files/${file}"

  mkdir -p "${chezmoi_src_dir}/${chezmoi_app_dir}"

  cat >"${chezmoi_src_dir}/${chezmoi_link_file}" <<EOS
{{ joinPath .chezmoi.sourceDir "dotfiles" "apps" "${app}" "files" "${file}" }}
EOS

  echo "Created chezmoi symlink template:"
  echo "  ${chezmoi_link_file}"
  echo "Will create symlink at:"
  echo "  ~/.config/${app}/${file} -> ~/.local/share/chezmoi/dotfiles/apps/${app}/files/${file}"
}
