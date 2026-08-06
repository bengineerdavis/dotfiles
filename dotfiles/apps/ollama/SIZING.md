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

### Linux specifics

- **Budget basis is VRAM, not system RAM**, when a discrete GPU is present —
  `ollama-models` reads `nvidia-smi`, then `rocm-smi`. A 16 GB card yields a
  ~10.7 GB budget after the 33% reserve, which gates out most of the manifest
  even if the host has 64 GB of system RAM.
- **Ollama can split a model across GPU and CPU.** The manifest's VRAM-only gate
  is deliberately conservative and will skip models that *would* run, slowly, in
  a hybrid split. Lower `ollama_ram_reserve_pct` if you want to allow that.
- **AMD/ROCm takes GGUF** (`linux` key), not the NVFP4 builds — so the
  pay-upfront KV behaviour above applies, and capping `num_ctx` matters more
  than it does on the Mac.
- **No MLX on Linux.** The lazy-allocation advantage is Apple-only; budget the
  full declared window.
