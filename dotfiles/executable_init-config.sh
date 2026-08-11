#!/usr/bin/env bash

# This script uses a template directory to jump-start new configuration modules
# Author: Ben Davis
# License: MIT

set -e

### Variables
TEMPLATE_MODULE_DIR="$PWD/template_dir"
APPS_DIR="$PWD/apps"

echo ''

### Helper functions
info () {
  printf "\n\r  [ \033[00;34m..\033[0m ] %s\n" "$1"
}

user () {
  printf "\n\r  [ \033[0;33m??\033[0m ] %s\n" "$1"
}

success () {
  printf "\n\r\033[2K  [ \033[00;32mOK\033[0m ] %s\n" "$1"
}

fail () {
  printf "\r\033[2K  [\033[0;31mFAIL\033[0m] %s\n" "$1"
  echo ''
  exit 1
}

# Module functions
# using rsync to cope with mac cp idiosyncracies
mk_module () {
  local module_path="$2"

  # rsync creates the destination itself, so there is nothing to pre-create here.
  # This used to run `mkdir -pv "./$1"`, which made an empty directory named after the
  # topic at the repo root — a stray sibling of apps/ that was never used.
  mkdir -pv "$module_path"
  rsync -a --progress "$TEMPLATE_MODULE_DIR/" "$module_path/"
}

### MAIN
main () {
  # Require a positional arg
  if [[ $# -lt 1 || -z "${1:-}" ]]; then
    fail "Usage: $0 <configuration_directory_name>"
  fi

  local module_name="$1"
  local module_path="$APPS_DIR/$module_name"
  info 'Preparing to make new dotfile config module'
  info "Creating new module: $module_name ... in $module_path ... "

  echo ''
  if ! mk_module "$module_name" "$module_path"; then
    fail "Creating module '$module_name' at '$module_path' unsuccessful"
  fi

  success "New module, '$module_name', at '$module_path', created."
}

# Pass through CLI args (instead of hardcoding "@")
main "$@"
