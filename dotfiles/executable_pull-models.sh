#!/usr/bin/env bash

PARALLEL=${PARALLEL:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)}

printf "%s\n" 3b 8b 14b   | xargs -P "$PARALLEL" -I {} ollama pull "ministral-3:{}" &
printf "%s\n" 250m 1b 3b  | xargs -P "$PARALLEL" -I {} ollama pull "granite4:{}" &
printf "%s\n" latest q4_K_M q8_0 bf16 | xargs -P "$PARALLEL" -I {} ollama pull "glm-4.4-flash:{}" &
printf "%s\n" 8x7b 8x22b  | xargs -P "$PARALLEL" -I {} ollama pull "mixtral:{}" &
printf "%s\n" e2b e4b 26b 31b | xargs -P "$PARALLEL" -I {} ollama pull "gemma4:{}" &
ollama pull devstral-small-2:24b &
ollama pull mistral-small3.1:24b &

wait
echo "All pulls complete"