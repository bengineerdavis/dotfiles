# Research assignment: local-first LLM stack — model selection, licensing, telemetry

## Your role

You are a research analyst producing a **decision document** for one person
running LLMs on their own hardware. You are not writing a survey or a blog post.
Every section must end in a recommendation someone can act on this week.

Today is **August 2026.** This field moves fast enough that anything older than
~6 months is suspect. Date every claim.

## What this unblocks

Four decisions are currently blocked on you:

1. Which **two cost-effective ("80/20") cloud models** to use as daily drivers,
   plus **one top-tier model** used chiefly to *assess* the other two.
2. Which **open-data / ethically-sourced** models to adopt beyond OLMo.
3. Whether outputs from large cloud models may **legally be used to fine-tune**
   local models — and if so, whose.
4. What to **log and how to sync it** across two machines to get better at
   prompting, agents, and automation.

## Operating rules

- **Primary sources first.** Model cards, provider ToS, official pricing pages,
  papers. Blog summaries only to find primaries.
- **Never launder a vendor claim as fact.** If a number comes from the vendor's
  own announcement, label it. Two real errors in this project came from trusting
  claims: a model card advertised audio the shipped build lacks, and a planning
  doc asserted a 512K context window for a model whose own files report 131K.
- **Prefer "no reliable source found" to a plausible guess.** An honest gap is
  useful; a confident wrong number costs days.
- **When sources disagree,** give the range and say who says what. Do not
  silently pick one.
- **Show arithmetic** for anything comparative — cost-per-quality especially.
  "Model X is a good value" is not an answer; a table with the division is.
- **Distinguish weights licence from API terms of service.** They routinely
  differ, and for output/distillation questions the ToS usually binds.
- **Distinguish weights-open from data-open.** Most "open" models disclose
  neither training data nor its provenance. This distinction is the whole point
  of question R2.

## Hard constraints — do not recommend anything that violates these

| | |
|---|---|
| Mac | Apple Silicon M4 Max, **36 GB unified**; ~16 GB resident to other apps, **~20 GB realistically free** |
| Linux | RTX 3090 (24 GB, **Ampere**) + RX 6900 XT (16 GB, RDNA2/ROCm); 32 GB RAM now → **128 GB** soon |
| Offline | Must work with no internet (power loss, travel) |
| Privacy | Sensitive data must not leave the local network; cloud only where **Zero Data Retention** is available |
| Runtime | **Ollama** — a model without an Ollama/GGUF build does not count as "local" |
| Use cases | research, thought experiments, technical support/troubleshooting, coding |

**Economic stance (the crux):** always prefer the cheaper model when the result
would be hard to distinguish from the best. The target is **two 80/20 models as
daily drivers + one frontier model reserved for assessment**, not a frontier
model used by default.

**Appetite:** this person would rather have *more* models available than fewer,
provided each has a distinct job. Do not optimise for a minimal set.

## Already established — do not re-derive; DO challenge

All measured directly on the hardware above. If your research contradicts any of
these, say so explicitly with sources — that is a valuable finding, not a
nuisance.

1. **NVFP4 and MLX are the same artifact.** `qwen3.6:27b-mlx` and
   `qwen3.6:27b-nvfp4` share an identical registry digest. NVFP4 is an open
   microscaling format; Ollama's MLX backend serves it on Apple Silicon. At
   **bf16** they diverge (`4b-mlx-bf16` ≠ `4b-bf16`).
2. **NVFP4 has no fast path on Ampere or RDNA2** — emulated via higher-precision
   kernels, no gain over BF16. Native FP4 begins at Blackwell (CC ≥ 10.0).
3. **Every gemma4 `-mlx` build drops vision and audio.** Verified by pulling
   both variants: `gemma4:e2b-it-qat` (GGUF) reports vision+audio;
   `gemma4:e2b-mlx-bf16` reports neither. Model cards do not reflect this.
4. **KV cache cost is architecture-driven, not size-driven.** Measured KB/token:
   `granite4:32b-a9b-h` ~19 (hybrid Mamba) · `glm-4.7-flash` ~50 ·
   `qwen3.6:27b-mlx` ~72 · **`ministral-3:3b` ~107** — the smallest model has
   the dearest context.
5. **MLX allocates KV lazily; GGUF preallocates at `num_ctx`.**
6. **`OLLAMA_FLASH_ATTENTION=1` + `OLLAMA_KV_CACHE_TYPE=q8_0` cuts KV ~57%**
   (glm-4.7-flash @131k ctx: 26 GB → 22 GB).
7. **Real prompt sizes**, 278 logged calls: p50 ≈ 934, p90 ≈ 4,591,
   p99 ≈ 65,535 input tokens.
8. **OpenRouter ZDR**: per-request `"provider": {"zdr": true}` or globally at
   `/settings/privacy`; machine-readable list at
   `GET https://openrouter.ai/api/v1/endpoints/zdr` (712 endpoints). ZDR
   **excludes first-party** Anthropic/OpenAI/Google endpoints, routing via
   Bedrock/Azure/Vertex instead, and does **not** cover plugins/tools.
9. **No mainstream leaderboard ranks the 27–35B class** this hardware runs.

---

# Questions

Priority order. **If you can only complete three, do R1, R2, R3.**

Each answer: **table first, prose second, recommendation last.**

## R1 — The 80/20 frontier (highest priority)

Build a comparison of cloud models available **via OpenRouter**. Cover at
minimum: `anthropic/claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4.5`,
`claude-fable-5`; OpenAI GPT-5.6 variants; `google/gemini-3.1-pro`,
`gemini-3.6-flash`; `deepseek/deepseek-v4-pro`, `deepseek-v4-flash`;
`z-ai/glm-5.2`; `moonshotai/kimi-k3`, `kimi-k2.7-code`; `minimax/minimax-m3`;
Qwen3.x Max.

Per model: **input $/Mtok · output $/Mtok · context window · benchmark scores
(name each) · ZDR available on OpenRouter · open vs closed weights.**

Then answer:

- Which models reach **≥85–90% of frontier quality at ≤25% of frontier cost**?
  Show the division.
- **Name the two 80/20 daily drivers and the one assessment model.** Justify
  against the four use cases specifically — not on a composite "intelligence"
  score. If the best pick differs per use case, say so and give a per-use-case
  answer rather than forcing one.
- Where does the cheap model **measurably break down**? Name task types where
  escalation is genuinely required, so the escalation rule can be written down.
- **Benchmark validity:** which benchmarks actually predict real-world coding
  and research performance, and which are saturated, contaminated, or gamed?

## R2 — Open-data / ethically-sourced models

This person specifically values models built from data used with permission or
under permissive licence, and wants **more options in this category**, sized for
the hardware above.

Check at least: **OLMo 3.x (Ai2)**, Common Pile / Comma, **K2 (LLM360)**,
**Marin (Stanford)**, Pythia, StarCoder2, SmolLM, Falcon, BLOOM, **IBM Granite**
(what is genuinely disclosed about its data?), NVIDIA Nemotron open-data
releases — plus anything newer you find.

Per model: **sizes · licence · what is actually disclosed about training data
(weights-open vs data-open) · Ollama/GGUF build available? · benchmark standing
vs mainstream models of the same size.**

Then: which belong on a 36 GB Mac and/or a 24 GB GPU, and **what is the honest
quality cost** of choosing open-data over the best model of the same size?

## R3 — Licensing for distillation and fine-tuning

The goal is to **fine-tune local models using feedback or outputs from larger
cloud models**. Determine whether that is permitted, per provider.

Cover: Anthropic, OpenAI, Google/Gemini, Meta Llama, Alibaba Qwen, DeepSeek,
Mistral, Zhipu/GLM, Moonshot/Kimi, MiniMax, Ai2 OLMo, IBM Granite.

Output: **provider | permitted? (yes / no / ambiguous) | exact clause quoted |
source URL | date checked.** Separate *weights licence* from *API ToS*. Flag
recent changes.

Then: **which models explicitly permit distillation**, so they can serve as the
teacher? An open-weight teacher that permits it may beat a better closed model
that forbids it — say which you would actually use.

## R4 — Evaluating the 27–35B local class

Mainstream leaderboards skip this class. Find sources that don't.

- Quality lost to **4-bit (q4_K_M / NVFP4 / MLX-4bit) vs q8_0 vs bf16** at
  27–35B — measured degradation, not folklore.
- Does **KV-cache quantisation** (q8_0, q4_0) degrade output quality, and at
  what context length does it begin to matter? (This stack now runs q8_0 KV.)
- Any credible independent comparison of: qwen3.6 (27b / 35b-a3b), gemma4
  (12b / 26b / 31b), glm-4.7-flash, granite4 / 4.1, olmo-3.1, devstral-small-2,
  deepseek-r1:32b, ministral-3, lfm2.5.

## R5 — What a solo practitioner should log

**Current state, measured — this corrects the assumption that the schema is
being filled:**

The `llm` CLI logs to SQLite (383 MB, 278 calls). Genuinely populated: model,
full prompt text, full response text, `input_tokens`, `output_tokens`,
`duration_ms`, timestamp, conversation id, attachments.

Empty in practice: **`response_json` (0 bytes — no provider metadata at all),
`token_details` 0/278, `options_json` 0/278, `resolved_model` 0/278,
`schema_id` 0/278, `system` 32/278.**

Absent entirely: **cost, task/project label, time-to-first-token,
success/quality signal, prompt version, and failed calls.**

**Coverage is the bigger problem:** only traffic through the `llm` CLI is
recorded. Claude Code, the `ori` harness, `ollama run`, and any direct API call
are invisible — so the log is a small, biased sample that over-represents ad-hoc
prompting and under-represents agentic work, which is where the optimisation
headroom probably is.

Research:

- **What should a solo practitioner instrument** to measurably improve prompting,
  agent design, and automation? Focus on metrics that change decisions. How do
  you attribute an outcome to a prompt or model change with **n = 1** and no A/B
  infrastructure?
- **How to capture *all* traffic**, not just CLI: is putting a logging proxy
  (LiteLLM proxy, or similar) in front of the Ollama server the right move, and
  what breaks? Does it work for Claude Code and OpenAI-compatible agent clients?
- **Local-first tools** — Langfuse, Phoenix/Arize, Helicone, OpenLLMetry,
  Braintrust: which run **fully offline**, and can any ingest an existing SQLite
  log rather than starting fresh?
- **Backfilling cost** into historical rows from model + token counts: is there
  a maintained price table to join against?

## R6 — Syncing an append-mostly SQLite log across two machines

Requirement: unified history across Mac and Linux, **offline-capable, no
mandatory cloud service**, tolerant of both machines writing while disconnected.

Compare: Syncthing on the raw file · Litestream · rqlite / dqlite ·
libSQL/Turso embedded replicas · git + periodic `.dump` · Mutagen · Unison ·
anything purpose-built.

Per option: **conflict behaviour · corruption risk under WAL · offline tolerance
· setup burden.** Recommend one and **state the failure mode being accepted.**

Also: `llm`'s schema uses autoincrement ids and a hash-keyed message tree — is
it safe to merge across machines, or does it need UUID rekeying first? This
determines whether to fix the schema *before* accumulating more history.

## R7 — Designing the role matrix

Current implementation routes by **role**, not model name, resolving to a
concrete model at shell init and validating declared capabilities against the
runtime (not the model card). Present roles: `chat`, `code`, `think`, `fast`,
`long`, `vision`, `audio`, `embed`, `escalate`. Only four have fallback chains,
and nothing consumes them yet.

Research how others structure this — LiteLLM router, OpenRouter presets/model
groups, Aider and Continue model roles, RouteLLM and cost-aware routers.

- **Which role dimensions earn their complexity, and which collapse in
  practice?** This person wants a richer matrix; tell them which axes are worth
  splitting on (task type? context length? latency? modality? cost tier?) and
  which are noise.
- Does **automatic cost-aware routing** (cheap model first, escalate on low
  confidence) work well enough to adopt? How is "should I escalate?" actually
  decided — self-reported confidence, a judge model, heuristics? Give evidence,
  not architecture diagrams.

## R8 — Privacy specifics still unverified

- Under OpenRouter ZDR, what **metadata** is retained (token counts, latency,
  model, timestamps) when content is not? Their docs are silent.
- Do any R1 candidates **train on API data by default**, and can that be
  disabled independently of ZDR?
- Any telemetry in **Ollama itself**? (The desktop app has been removed here;
  the Homebrew formula's server is used, started by a user-owned launchd agent.)

## R9 — Local runtime questions

- **Dual-instance Ollama** (one CUDA-pinned, one ROCm-pinned, separate ports) on
  a mixed 3090 + 6900XT box: known issues? Can any single client pool both
  cards? Is `HSA_OVERRIDE_GFX_VERSION=10.3.0` still required for gfx1030 on
  current ROCm?
- Any upstream signal that **MLX builds will gain vision/audio**, or is GGUF
  permanently required for multimodal on Apple Silicon?
- With **128 GB system RAM + a 24 GB GPU**, realistic **tokens/sec** for a
  120B-class MoE (`gpt-oss:120b`, `qwen3.5:122b-a10b`) split CPU/GPU. Numbers,
  not "it works".

---

## Output contract

1. **Executive answer** — the two 80/20 models + one assessment model, and the
   open-data models to adopt. Lead with this.
2. One section per R-number, tables first, recommendation last.
3. **Corrections** — anything in *Already established* your research
   contradicts, with sources.
4. **Confidence** per recommendation (high / medium / low) **and what would
   change your mind.**
5. **Open questions** — what you could not resolve, and what source would settle
   it.

## Before you return

Check yourself against these:

- Does every comparative claim show its arithmetic?
- Is every vendor-sourced number labelled as such?
- Have you separated weights licence from API ToS in R3?
- Have you separated weights-open from data-open in R2?
- Does each recommendation survive the hard constraints (36 GB Mac, 24 GB GPU,
  offline, ZDR)?
- Have you said what you *couldn't* find, rather than filling gaps with
  plausible text?
