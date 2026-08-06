# Ollama runtime tuning — memory-pressure defaults.
#
# Measured on this MacBook Pro (36 GB unified) with NO model loaded:
#   wired + active (genuinely resident)  16 GB
#   swap already in use                 5.5 GB
#   free                                0.1 GB
#
# The machine is already swapping before ollama starts, so ollama's defaults —
# keep a model resident for 5 minutes, allow several at once — are enough to
# push it over. These two settings make a finished model release memory
# promptly instead of lingering.
#
# Scoped to macOS deliberately: on a large-memory Linux host (128 GB) holding
# several models is desirable, and these limits would only get in the way.
# See apps/ollama/SIZING.md for the measurements and apps/ollama/MODELS.md for
# which models fit alongside normal apps.
# ⚠ THESE ONLY APPLY TO A SHELL-LAUNCHED `ollama serve`.
# The Ollama.app starts its own server and does NOT inherit your shell
# environment — verified by reading the running server's env, which carries
# OLLAMA_CONTEXT_LENGTH=65536 from the app's own settings database
# (~/Library/Application Support/Ollama/db.sqlite, `settings.context_length`)
# rather than from here. To change the app's behaviour, use its settings UI, or
# `launchctl setenv NAME VALUE` and restart the app. See SIZING.md.
if [[ "$OSTYPE" == darwin* ]]; then
  # Two smalls, or one large, plus a companion — see MODELS.md for the tiers.
  # A count is the only lever ollama offers; it cannot cap by size, so the
  # discipline of not pairing two large models still has to be yours. Ollama's
  # scheduler is memory-aware and evicts LRU rather than overcommitting, but it
  # does not know ~16GB of this machine is already spoken for by other apps.
  export OLLAMA_MAX_LOADED_MODELS=3

  export OLLAMA_KEEP_ALIVE=60s        # unload quickly rather than after 5m

  # Must match ollama_target_ctx_tokens in defaults/main.yaml or the budget is
  # fiction. Ollama auto-scales its own default from available memory
  # ("4k/32k/256k based on VRAM") and picks 65536 here — double what the
  # manifest budgets, and doubly costly when holding several models. 32K keeps
  # 33 of 36 models inside budget where 64K keeps only 28. Raise it per request
  # with `options.num_ctx` when a job genuinely needs more.
  export OLLAMA_CONTEXT_LENGTH=32768
fi
