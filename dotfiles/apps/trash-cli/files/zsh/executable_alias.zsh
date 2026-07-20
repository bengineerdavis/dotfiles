# alias tp='trash-put -v'
# alias te='trash-empty -v'
# # trash-list + trash-restore doesn't have a verbose option, so we just alias it to tl
# alias tl='trash-list'
# alias trr='trash-restore'   # not `tr` — that's coreutils


# 2. Detect Tool and Set Aliases
if command -v trash-put &> /dev/null && [[ "$(uname -s)" == "Darwin" ]]; then
    # PYTHON trash-cli (pip install trash-cli) - Cross-platform
    alias tp='trash-put -v --trash-dir "$TRASH_DIR"'
    alias tl='trash-list --trash-dir "$TRASH_DIR"'
    # NOTE: do NOT alias `tr` — it shadows the coreutils text utility used all
    # over shell pipelines. Use `trr` for trash-restore.
    alias trr='trash-restore --trash-dir "$TRASH_DIR"'
    alias te='trash-empty -v --trash-dir "$TRASH_DIR"'
    
else
    # FALLBACK (Safety)
    alias tp='rm -i'
    echo "Warning: No trash utility found. 'tp' aliased to 'rm -i'."
fi

