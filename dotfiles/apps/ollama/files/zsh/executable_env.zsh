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
if [[ "$OSTYPE" == darwin* ]]; then
  export OLLAMA_MAX_LOADED_MODELS=1   # never hold two large models at once
  export OLLAMA_KEEP_ALIVE=60s        # unload quickly rather than after 5m
fi
