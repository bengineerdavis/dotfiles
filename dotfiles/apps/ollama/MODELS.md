# Local model quick reference

Which model to reach for, by task. Every number here is **measured** on this
machine with `ollama show` — parameter counts, context windows and capabilities
come from the model files themselves, not from marketing copy.

Regenerate after any manifest change:

```sh
for m in $(ollama list | awk 'NR>1&&NF{print $1}' | sort); do
  ollama show "$m" | awk -v n="$m" '/context length/{c=$NF} /parameters/{p=$NF}
    END{printf "%-46s %-8s %s\n", n, p, c}'
done
```

Budget on this Mac: 36 GB unified memory, **24 GB usable** (33% reserved). One
large model at a time, or one large + one small resident together.

---

## Pick by task

| Task | Model | Size | Context | Why this one |
|---|---|---|---|---|
| **General default** | `qwen3.6:27b-mlx` | 19 GB | 262K | Best all-rounder: dense 27.4B, vision + thinking + tools, native MLX |
| **Same but faster** | `qwen3.6:35b-mlx` | 21 GB | 262K | 35.1B MoE, only **3B active** — far quicker per token, more total knowledge |
| **Coding** | `qwen3.6:27b-coding-nvfp4` | 19 GB | 262K | Coding-tuned qwen3.6. NVFP4 *is* an MLX build — runs native on Metal |
| **Coding, faster** | `qwen3.6:35b-a3b-coding-nvfp4` | 21 GB | 262K | MoE coding variant, 3B active |
| **Whole-repo coding** | `devstral-small-2:24b` | 15 GB | **393K** | Longest context of any coding model here; agent/codebase-oriented |
| **Repo-scale anything** | `granite4:32b-a9b-h` | 19 GB | **1,048,576** | **1M context** — 4× anything else. MoE, 9B active. Tools, no thinking |
| **Hard reasoning** | `deepseek-r1:32b` | 19 GB | 131K | RL-trained reasoning lineage, thinking + tools |
| **Reasoning, long input** | `glm-4.7-flash:q4_K_M` | 19 GB | 202K | 29.9B, thinking + tools, more context than r1 |
| **Open reasoning** | `olmo-3.1:32b-think-q4_K_M` | 19 GB | 65K | Fully-open weights *and* training data — use when provenance matters |
| **Cheap reasoning** | `gpt-oss:20b` | 13 GB | 131K | Smallest thinking model that is still strong; native MXFP4 |
| **Agent loop, small** | `ministral-3:3b-…-q8_0` | 4.5 GB | **262K** | Best context-per-GB on the box. Vision + tools |
| **Agent loop, mid** | `ministral-3:8b-…-q8_0` | 9.9 GB | 262K | Same, with more headroom for tool reasoning |
| **Fastest agent steps** | `lfm2.5:8b-a1b-q8_0` | 9.0 GB | 128K | 8.5B MoE with **1B active** — lowest latency per step, thinking + tools |
| **Vision, small** | `qwen3-vl:8b-instruct-q8_0` | 9.8 GB | 262K | Dedicated VL model; qwen3.6 has no small member |
| **Vision, large** | `qwen3.6:27b-mlx` | 19 GB | 262K | Vision is built in — no separate VL model needed at this size |

### Embeddings / RAG

| Model | Size | Context | Use when |
|---|---|---|---|
| `qwen3-embedding:8b-fp16` | 15 GB | 40K | Highest quality retrieval |
| `qwen3-embedding:4b-fp16` | 8.0 GB | 40K | Good balance — sensible default |
| `qwen3-embedding:0.6b-fp16` | 1.2 GB | 32K | Bulk indexing, throughput-bound |
| `bge-m3:567m-fp16` | 1.2 GB | 8K | Strong multilingual retrieval |
| `embeddinggemma:300m-bf16` | 621 MB | 2K | Short snippets, tightest footprint |

---

## Things worth knowing

**`granite4:32b-a9b-h` has a 1M context window** — 1,048,576 tokens, four times
the 262K of the qwen family and the standout capability in this set. It only has
`tools` (no thinking, no vision), so it's the tool of choice for *ingesting*
something enormous, not for reasoning hardest about it.

**Context ≠ free.** At 262K the KV cache, not the weights, dominates memory. The
small agent models are pinned to `q8_0` rather than full precision precisely to
buy that headroom. A 4.5 GB model can still exhaust 24 GB if you actually fill
its window.

**MoE vs dense.** `35b-a3b` is 35.1B total but activates 3B per token: much
faster generation and cheaper long-context, at somewhat lower per-token quality
than the dense 27.4B. Prefer the MoE for agent loops and long generations, the
dense model for single hard answers.

**Old context assumptions don't hold.** `lfm2:24b` is only 32K — its successor
`lfm2.5:8b-a1b` has 128K in a third of the size. `olmo-3.x` is 65K, the shortest
of the large models.

### ⚠ The gemma4 MLX builds drop vision and audio

Verified by pulling both builds of the same model and comparing directly:

| tag | capabilities |
|---|---|
| `gemma4:e2b-it-qat` (GGUF) | completion, **vision**, **audio**, tools, thinking |
| `gemma4:e2b-mlx-bf16` (MLX) | completion, tools, thinking |

Gemma 4 is the only **audio-capable** family in the library, and the MLX
packaging is text-only. The manifest currently prefers MLX on macOS, so *that
capability is not currently available locally*. This is the one place where the
"always prefer MLX on mac" rule costs something real.

To get it back, switch the darwin key for gemma4 to the GGUF `-it-` builds
(`gemma4:e4b-it-bf16`, `gemma4:31b-it-q4_K_M`, …). They run fine on Metal via
llama.cpp — just not through MLX.

---

## When to escalate off the machine

Three tiers, and they do genuinely different jobs:

| Layer | Cost | Reach for it when |
|---|---|---|
| **Local** (`ollama`) | free | Default. Private, offline, zero marginal cost |
| **`llm` + OpenRouter** | per token | One-off prompts, scripting, piping — no harness needed |
| **`ori`** ([topic](../ori/README.md)) | per token | You want a *full agentic coding harness* (Claude Code, Codex, opencode, Hermes) on a remote model |

### Don't pay for what you already have

Local already covers these well — escalating buys little:

general chat · coding at 27–35B · 262K context · vision to 27B · embeddings ·
fast small agents · **1M-token ingestion** (`granite4:32b-a9b-h` beats most
remote context windows outright)

### Worth escalating for

| Gap | Remote model | Why |
|---|---|---|
| **Reasoning ceiling** | `anthropic/claude-opus-5`, `google/gemini-3.1-pro-preview` | Largest local is 35B with 3B active — a different class of problem-solving |
| **Best harness fit** | `anthropic/claude-sonnet-5` via `ori claude` | Claude Code is Anthropic's own harness; least friction, strongest tool-calling |
| **Successor to a local model** | `z-ai/glm-5.2` | 976K context. The direct next generation of your local `glm-4.7-flash`, and **cloud-only** — impossible to download |
| **Successor to a local model** | `deepseek/deepseek-v4-pro` | Next generation of your local `deepseek-r1:32b`, also cloud-only |
| **Coding beyond 24 GB** | `moonshotai/kimi-k2.7-code`, `minimax/minimax-m3` | Open weights far too large to hold locally |
| **Audio** | `openai/gpt-audio` | You currently have **no** local audio model — see the gemma4 note above |
| **Low-latency interactive** | `anthropic/claude-haiku-4.5`, `google/gemini-3.6-flash` | Faster than a 27B on Metal when responsiveness matters more than privacy |

The two "successor" rows are the strongest case for remote: same families you
already run, at generations that have no downloadable weights at all.

### A practical split

- **`ori claude` on a frontier model** — unfamiliar codebase, hard debugging, architecture work
- **Local `qwen3.6:27b-coding-nvfp4`** — routine edits, refactors, anything private or offline
- **Local `ministral-3:3b`** — cheap high-volume agent loops where 262K context matters more than raw quality

## Running two at once

24 GB usable, so a large + small pair fits:

```
qwen3.6:27b-mlx (19)  +  ministral-3:3b (4.5)   = 23.5 GB   ← tight but works
devstral-small-2 (15) +  lfm2.5:8b-a1b (9.0)    = 24.0 GB   ← coding + fast agent
gpt-oss:20b (13)      +  qwen3-vl:8b (9.8)      = 22.8 GB   ← reasoning + vision
```

Ollama unloads idle models automatically; `OLLAMA_MAX_LOADED_MODELS` controls how
many stay resident.
