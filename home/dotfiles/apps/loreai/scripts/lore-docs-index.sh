#!/bin/sh
# apps/loreai/scripts/lore-docs-index.sh
#
# Regenerate the documentation index for lore, from the local fork.
#
# Why this exists: apps/loreai/DOCS.md carries an index of lore's documentation
# so an agent can find the right page without crawling the tree. That index goes
# stale whenever upstream moves a page or renames a title. Rather than re-deriving
# it by hand, this prints the current table to stdout; paste it over the index
# section in DOCS.md, or diff it to see what moved.
#
# Read-only. Touches nothing. Run from anywhere.
#
# Usage:
#   scripts/lore-docs-index.sh              # table to stdout
#   scripts/lore-docs-index.sh --check      # exit 1 if DOCS.md's index differs
#
# The fork, not the installed binary, is the source: DOCS.md states the same.

set -eu

REPO="${LOREAI_FORK:-$HOME/code/forks/loreai}"
DOCS_DIR="$REPO/packages/website/src/content/docs/docs"
DOCS_FILE="${DOCS_FILE:-$(dirname "$0")/../DOCS.md}"

if [ ! -d "$DOCS_DIR" ]; then
  printf 'lore-docs-index: no docs at %s\n' "$DOCS_DIR" >&2
  printf '  Set LOREAI_FORK, or clone the fork:\n' >&2
  printf '  gh repo clone bengineerdavis/loreai %s\n' "$REPO" >&2
  exit 2
fi

# emit_index <dir> <label>: print a markdown table for every *.md under <dir>.
emit_index() {
  _dir=$1
  _label=$2
  printf '%s\n\n' "$_label"
  printf '| Page | File |\n|---|---|\n'
  for _f in "$_dir"/*.md; do
    [ -f "$_f" ] || continue
    _base=$(basename "$_f")
    # title: frontmatter, else the first H1, else the basename.
    _title=$(sed -n 's/^title:[[:space:]]*//p' "$_f" | head -1)
    if [ -z "$_title" ]; then
      _title=$(sed -n 's/^#[[:space:]]*//p' "$_f" | head -1)
    fi
    [ -n "$_title" ] || _title="$_base"
    _filecell=$(printf '%s%s%s' '`' "$_base" '`')
    printf '| %s | %s |\n' "$_title" "$_filecell"
  done
  printf '\n'
}

print_header() {
  _commit=$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo unknown)
  _date=$(date +%Y-%m-%d)
  _version=$(lore --version 2>/dev/null | head -1 || echo 'not installed')
  printf 'Generated %s from fork %s\n' "$_date" "$_commit"
  printf 'Installed binary: %s\n\n' "$_version"
}

if [ "${1:-}" = "--check" ]; then
  # Real comparison, not a spot-check: extract every doc filename the generated
  # index mentions, and every filename DOCS.md's index mentions, then diff the
  # two sets. A file present in one and not the other is drift worth seeing.
  _gen=$(mktemp)
  _have=$(mktemp)
  trap 'rm -f "$_gen" "$_have"' EXIT

  {
    emit_index "$DOCS_DIR" 'core'
    emit_index "$DOCS_DIR/guides" 'guides'
  } | grep -o '[a-z0-9-]*\.md' | sort -u > "$_gen"

  # Only the index section of DOCS.md: between the index heading and the next
  # top-level heading that is not part of it.
  # The File column only (second pipe-delimited cell), so neither prose cells
  # nor the surrounding narrative can introduce a false filename.
  sed -n '/^## Documentation index/,/^## Load-bearing facts/p' "$DOCS_FILE" 2>/dev/null \
    | awk -F'|' 'NF>=4 {print $3}' \
    | grep -o '[a-z0-9-]*\.md' | sort -u > "$_have"

  if [ ! -s "$_have" ]; then
    printf 'lore-docs-index: no index section found in %s\n' "$DOCS_FILE" >&2
    exit 2
  fi

  if diff -u "$_have" "$_gen" > /dev/null 2>&1; then
    printf 'docs index is current — %s files, no drift\n' "$(wc -l < "$_gen" | tr -d ' ')"
    exit 0
  fi

  printf 'docs index is stale. Files in DOCS.md but not upstream, or vice versa:\n\n' >&2
  diff -u "$_have" "$_gen" | sed -n '3,$p' >&2
  printf '\nRegenerate with: %s\n' "$0" >&2
  exit 1
fi

print_header
emit_index "$DOCS_DIR" '### Core pages'
emit_index "$DOCS_DIR/guides" '### Guides'
