# Local-first sizing: how much model fits in how much RAM

Everything here was **measured on this hardware**, not taken from a sizing
chart. The headline result contradicts the usual advice, so the method matters.

**Method.** Load a model with a given `num_ctx`, read resident memory from
`ollama ps`, subtract the weights. For MLX, also send a genuinely long prompt
(41,683 tokens) because MLX allocates lazily — a short prompt understates it.

---

## The finding that matters most

**GGUF pays for the window you declare. MLX pays for the tokens you use.**

| model | format | weights | 4K | 64K | 128K | 262K |
|---|---|---|---|---|---|---|
| `qwen3.6:27b-mlx` | MLX | 19 GB | 19 | 19 | — | **19** ¹ |
| `glm-4.7-flash:q4_k_m` | GGUF | 19 GB | 19 | 22 | 26 | — |
| `granite4:32b-a9b-h` | GGUF | 19 GB | 19 | 21 | — | 24 |
| `ministral-3:3b-…-q8_0` | GGUF | 4.5 GB | 4.2 | 11 | — | **33** |

¹ With a near-empty cache. Fed a real 41,683-token prompt, the same model grew
to **22 GB** — so MLX is *not* free at long context, it just bills on use.

The practical consequence: with GGUF, setting `num_ctx=131072` costs you ~7 GB
even for a two-line chat. With MLX you can leave the window wide open and only
pay as the conversation grows.

## KV cost is about architecture, not model size

Derived from the deltas above (two independent points each, both linear):

| model | params | KV per token |
|---|---|---|
| `granite4:32b-a9b-h` | 32.2B | **~19 KB** |
| `glm-4.7-flash` | 29.9B | ~50 KB |
| `qwen3.6:27b-mlx` | 27.4B | ~72 KB |
| `ministral-3:3b` | 3.8B | **~107 KB** |

The 3.8B model costs **5.6× more per token** than the 32B one. Granite's hybrid
(Mamba-style) layers are why it is so cheap; a small transformer with a big
window is the worst case. *Never assume a small model has a small footprint at
long context.*

This also shows the common guidance — "budget an extra 10–20% for long context"
— is badly wrong at the top end. For `ministral-3:3b` at 262K it is **+644%**.

## Advertised windows are mostly unreachable on 36 GB

Metal can address ~27 GB here (75% default of 36 GB). Max context before you
hit that ceiling:

| model | advertised | **actually usable** |
|---|---|---|
| `granite4:32b-a9b-h` | 1,048,576 | **~400K** |
| `ministral-3:3b` | 262,144 | ~200K |
| `glm-4.7-flash` | 202,752 | ~155K |
| `qwen3.6:27b-mlx` | 262,144 | ~110K |

~400K on granite4 is still the best local long-context option by a distance —
but it is not the 1M on the box.

---

## Recommendation for this Mac (M4 Max, 36 GB)

| Use | Pick | Why |
|---|---|---|
| Everyday driver | `qwen3.6:27b-mlx` | 19 GB resident, lazy KV, full capability set |
| Long documents / repo ingestion | `granite4:32b-a9b-h` | ~19 KB/token — 4× cheaper context than anything else |
| High-volume agent loops | `ministral-3:3b` **capped at ~32K** | Cheap to run, but ruinous if you open its full window |
| Never | any GGUF at `num_ctx` ≥ 128K alongside another model | 26 GB + anything exceeds the Metal cap |

**Prefer MLX**, and not only for speed: lazy allocation is what makes a wide
window affordable.

**Cap `num_ctx` on GGUF models deliberately.** The default is generous and you
pay for it upfront. 8–32K covers most work.

**The manifest's budget gate does not model this.** `size_gb` counts *weights
only*, so a model that passes the 24 GB budget can still blow past it once the
context fills. Treat `size_gb` as a floor, not a guarantee.

Raising the Metal cap is possible (`sudo sysctl iogpu.wired_limit_mb=30000`) but
starves the OS; 27 GB of 36 GB is a sensible default and this doc assumes it.

---

## Sizing any machine (including the Linux box)

Rule of thumb that matches the measurements: **~0.6 GB per billion parameters at
Q4**, ~1.1 GB/B at Q8, plus KV from the table above, plus 2–4 GB for the OS.

| RAM / VRAM | Comfortable ceiling | Notes |
|---|---|---|
| 8 GB | 3–4B Q4, 8K ctx | Toy tier |
| 16 GB | 7–9B Q4, 32K ctx | Practical minimum for real work |
| 24 GB | 14B Q4, or 8B Q8 | 27B Q4 fits weights but leaves no context room |
| 32 GB | 27–32B Q4, ~32K ctx | Comfortable single-model tier |
| **36 GB (this Mac)** | 27–35B Q4 + ~100K ctx | Or a small model with a very long window |
| 48 GB | 32B Q4 + long ctx | Or 70B Q4, tight |
| 64 GB | 70B Q4 comfortably | Two models resident |
| 128 GB | 120B Q4 / 70B Q8 | Frontier-adjacent locally |

## The Linux box: RTX 3090 + RX 6900 XT, 32 GB → 128 GB

Discrete VRAM, so unlike the Mac none of it is shared with system RAM.

| | VRAM | arch | native FP4/FP8? |
|---|---|---|---|
| RTX 3090 | 24 GB | Ampere, cc 8.6 | **No** — emulated |
| RX 6900 XT | 16 GB | RDNA2, gfx1030 | No |

### Your 3090 must not use the NVFP4 builds

Native FP4 tensor cores start at Blackwell (cc 10.0 datacenter / 12.0 consumer).
On Ampere and Ada, FP4 and FP8 are **emulated via higher-precision kernels with
no latency advantage over BF16** — so an nvfp4 build on a 3090 is strictly worse
than the same model as GGUF.

`linux_nvidia` therefore means *"has real FP4 silicon"*, not *"is an NVIDIA
card"*. `ollama-models` reads `nvidia-smi --query-gpu=compute_cap` and falls
through to the universal `linux` GGUF key on anything pre-Blackwell:

| host | resolves to |
|---|---|
| RTX 3090 (8.6) · RTX 4090 (8.9) | `linux` — GGUF |
| RTX 5090 (12.0) · B200 (10.0) | `linux_nvidia` — NVFP4 |
| RX 6900 XT | `linux_amd` → `linux` — GGUF |

### Two GPUs, two backends — ollama uses one

Ollama selects a single backend per server; it will **not** pool 24 + 16 = 40 GB
across CUDA and ROCm. Treat the 3090 as the model GPU. To use the 6900 XT at the
same time, run a second ollama instance pinned with `HIP_VISIBLE_DEVICES` on a
different `OLLAMA_HOST` port — useful for keeping embeddings or a 3B agent model
resident without evicting the main model.

### The default reserve is wrong for discrete VRAM

`ollama_ram_reserve_pct: 33` exists because unified memory is shared with the
OS. A dedicated GPU only needs a little headroom for display. At 33% the 3090
budgets just **16.1 GB**, which gates out most of the interesting models:

| | budget @ 33% | budget @ 10% |
|---|---|---|
| RTX 3090 (24 GB) | 16.1 GB | **21.6 GB** |
| RX 6900 XT (16 GB) | 10.7 GB | 14.4 GB |

At 16.1 GB you lose `qwen3.6:27b-q4_K_M` (17), `glm-4.7-flash` (19),
`granite4:32b-a9b-h` (19) and `granite4.1:30b` (17) — all of which fit at 10%.
Set `ollama_ram_reserve_pct: 10` in a host var for that machine.

Caveat: the budget gates **weights only**. `glm-4.7-flash` at 19 GB plus a 128K
window needs ~26 GB — past the 3090's 24 GB. On Linux there is no MLX, so KV is
preallocated at `num_ctx`; cap it at 32K unless you have measured otherwise.

### What the 128 GB upgrade actually buys

Not bigger GPU models — VRAM is unchanged. It buys **CPU and split inference**,
and the sweet spot there is **large MoE models**, because only a fraction of
parameters activate per token:

| model | size | active | fits 128 GB RAM |
|---|---|---|---|
| `qwen3.5:122b-a10b-q4_K_M` | 81 GB | 10B | ✅ |
| `gpt-oss:120b` | 65 GB | ~5B | ✅ |

A 122B dense model on CPU would be unusable; at 10B active it is genuinely
tolerable. That is the one class of model the 128 GB unlocks that neither GPU nor
the Mac can touch.

**Both are already in the manifest** as `linux`-only members carrying
`basis: ram`. That flag gates them against system RAM instead of VRAM —
otherwise the 24 GB card would veto an 81 GB model on a 128 GB host. Verified:

| host | result |
|---|---|
| Mac 36 GB | not offered (no `darwin` key) |
| Linux, 32 GB RAM — today | **skipped** (81 GB > 21 GB budget) |
| Linux, 128 GB RAM — after upgrade | **installs**, both |

So they switch themselves on when the RAM lands. Nothing to change.

> ⚠ **The reserve is one number serving two bases.** Dropping
> `ollama_ram_reserve_pct` to 10 for the 3090's VRAM also loosens the *RAM* gate
> to ~115 GB, which would leave only ~13 GB for the OS and KV cache under an
> 81 GB model. At the default 33% the RAM budget is ~86 GB, which is the right
> shape. If you lower the reserve for the GPU, re-check that the 120B members
> still leave headroom — or pin them with an explicit smaller `size_gb`.

At 32 GB today, keep everything inside the 3090's 24 GB and treat CPU offload as
a fallback, not a plan.
