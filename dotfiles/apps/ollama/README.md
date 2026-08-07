# Ollama App Module

My [Ollama](https://ollama.com/) topic — installs the runtime and keeps a
declarative, OS-aware set of models in sync.

## Model management (the important part)

The model set is **declarative**. The single source of truth is the manifest at
[`defaults/main.yaml`](defaults/main.yaml) (`ollama_models`), organized by model
family. It is applied by the [`ollama-models`](files/ollama-models) CLI, which
the install/upgrade tasks shell out to and which is symlinked onto `PATH` as
`~/bin/ollama-models`.

### Editing the set

Edit the manifest directly:

- **add a model** → copy a line under its family; set the per-host tags + `size_gb`
- **add a family** → add a new `family-name:` key with a list of members. A family
  must appear **exactly once** — duplicate YAML keys silently discard the earlier
  block, so put variants (e.g. qwen3.6's coding builds) inside their own family
- **drop a model** → delete/comment its line. Upgrades stop refreshing it, but
  already-pulled weights are **not** auto-deleted (see `prune` below)
- **keep a non-manifest tag** → add it to `ollama_prune_keep` (bare `:latest`
  aliases, hand-pinned experiments). `prune` never lists it; `sync` never pulls it

### Commands

```sh
ollama-models status              # installed / missing / skipped-oversized, per family
ollama-models sync                # pull manifest models that are missing (first-run behavior)
ollama-models sync --refresh      # update to latest — re-pulls only models whose
                                  #   upstream manifest digest changed (unchanged = skipped)
ollama-models sync --dry-run      # print what would be pulled, pull nothing
ollama-models check               # diff each family's upstream tags vs the manifest;
                                  #   flags NEW/unknown precision keywords (future formats)
ollama-models check --next-gen    # additionally probe for newer family generations,
                                  #   flagging any that are cloud-only (no local weights)
ollama-models prune               # list installed models NOT in the manifest (orphans)
ollama-models prune --remove      # delete those orphans (confirmed)
```

These map onto the lifecycle: `install`/`provision` runs `sync` (pull missing),
`upgrade` runs `sync --refresh` (update changed to latest).

**Models are "attachments" — gated behind the `full` profile.** A bare or
`minimal` run installs apps only; models pull only under `full` (or the
`attachments` tag). The profile is resolved by `bootstrap/profile.sh`
(`update.sh full` / `update.sh minimal`) and gated in `playbook.yaml` via
`ansible_run_tags`.

> **Open TODO:** dropping a model from the manifest does not yet auto-uninstall
> its weights on upgrade. `prune --remove` is the manual path; auto-reconcile on
> upgrade is a deliberate future decision (risk of deleting large weights).

## Per-OS / per-hardware tags

A member declares one tag per host key. The CLI resolves the **most specific key
the host matches**, falling back down the chain — so a family with no
hardware-specific build just declares `darwin` + `linux` as before:

| Key | Host | Build it selects |
|---|---|---|
| `darwin` | Apple Silicon | MLX (native Metal execution) |
| `linux_nvidia` | NVIDIA CUDA | NVFP4 (Blackwell-native 4-bit) |
| `linux_amd` | AMD ROCm | optional override; omit to inherit `linux` |
| `linux` | ROCm + CPU, and any unmatched host | universal GGUF baseline |

Vendor detection is automatic: `nvidia-smi` → `rocm-smi` → `/sys` PCI vendor id
(`0x10de` / `0x1002`), the same probe the ansible topic uses. NVIDIA wins on a
mixed box because NVFP4 is the fastest build shipped.

Only families that upstream actually publishes arch-specific builds for
(**qwen3.6, qwen3.5, gemma4**) carry the split. GGUF-only families (glm, granite,
lfm2, olmo, deepseek-r1, devstral, qwen3-vl, embeddings) keep the plain
`darwin`/`linux` pair — one GGUF serves Metal, CUDA, ROCm and CPU alike.

### Precision rules

| Family kind | Model size | macOS | NVIDIA | AMD / CPU |
|---|---|---|---|---|
| arch-split | small (≤4B) | `-mlx-bf16` | `-bf16` | `-bf16` |
| arch-split | large (>4B) | `-mlx` | `-nvfp4` | `-q4_K_M` |
| GGUF-only | small / large | full precision · fp8 if it fits budget, else fp4 floor | ← same | ← same |
| embeddings | any | full precision, identical tag on every host | ← same | ← same |

`-mxfp8` (8-bit, ~1.6× larger) is used **only** where no arch-optimized 4-bit
exists upstream — currently the qwen3.6 *coding* members, which ship no GGUF
build at all, so AMD/CPU falls back to MXFP8 (31–38 GB) and is budget-gated off
anything smaller than ~32 GB VRAM.

### Small / long-context agents

A dedicated category for tool-calling models small enough to stay resident for a
whole agent loop. Context lengths are measured with `ollama show`, not taken from
marketing copy:

| model | size | context | capabilities |
|---|---|---|---|
| `ministral-3:3b` | 5 GB | 262K | tools, vision |
| `ministral-3:8b` | 10 GB | 262K | tools, vision |
| `lfm2.5:8b-a1b` | 9 GB | 125K | tools, thinking (MoE, 1B active) |
| `qwen3.5:4b` / `:9b` | 9 GB | 262K | tools, vision, thinking |
| `granite4.1:3b` / `:8b` | 7 / 10 GB | 128K | tools |
| `gemma4:e4b` | 16 GB | 128K | tools, thinking, vision, audio |

These are pinned to **q8_0**, deliberately deviating from the small→full-precision
rule: at 125–262K context the KV cache, not the weights, dominates memory, so
halving the weights buys the context headroom that actually limits an agent run.
All are GGUF-only upstream, so they carry no hardware split.

Considered and rejected: `laguna-xs-2.1` (256K, tools+thinking — but 19–20 GB and
no 4-bit MLX build, so not "small"); `nemotron3:33b` (28 GB, over a 24 GB budget);
`lfm2.5-thinking:1.2b` (731 MB, but only 32K usable context).

> **macOS always gets MLX.** Every `darwin` tag in an arch-split family is an MLX
> build — no exceptions. Upstream ships no `-coding-mlx`, so the qwen coding
> members are declared **linux-only** (no `darwin` key) rather than falling back
> to NVFP4: on Metal that would only run by dequantising, i.e. slower than the
> plain `27b-mlx` for no quality gain. On mac, coding is served by
> `qwen3.6:27b-mlx` plus the dedicated `devstral-small-2:24b`.
> `ollama-models check` will surface a `-coding-mlx` tag if one ever appears.

**Budget gating:** `size_gb` is either a scalar (same footprint everywhere) or a
mapping of host key → GB when the per-hardware builds differ materially (a
mapping missing the active key falls back to its **largest** entry, so the gate
stays conservative). It is checked against a runtime budget of
`total − ollama_ram_reserve_pct` (default 33%). Anything larger is skipped with a
log line, so the same manifest works on a 16 GB laptop and a 128 GB box. On macOS
the basis is unified system RAM; on Linux with a discrete GPU it is **VRAM**
(`nvidia-smi` / `rocm-smi`), falling back to system RAM for CPU inference.

### Cloud tags are refused

Ollama's tag lists mix **hosted-only** tags in with real builds, and they look
like ordinary variants: `gemma4:31b-cloud`, `gpt-oss:20b-cloud`,
`qwen3.5:397b-cloud`, `deepseek-v4-flash:0731-cloud`. Ollama routes these to its
own servers and stores **no weights on disk**, so they can never satisfy a
manifest whose whole point is a local, offline, budget-gated model set.

They are rejected at every surface, and always with the reason attached:

| surface | behaviour |
|---|---|
| `check` | never suggests a cloud tag as an upstream addition |
| `check --next-gen` | prints `(cloud-only — no local weights)` next to the hit |
| `sync` | `CLOUD … NOT PULLED — cloud-only: hosted on ollama.com…`, counted as `refused-cloud=N` |
| `status` | state `CLOUD(never)`, plus a footer saying it will never install |

So if you add one by mistake, `status` tells you *why* it isn't in `ollama list`
instead of leaving it at `MISSING` forever. Detection covers both `:cloud` and
any `-cloud` suffix; a model merely *named* something like `cloudy:8b` is not
affected.

> Worth knowing: several genuinely newer generations — `glm-5.1` (198K ctx),
> `glm-5.2` (976K ctx), `deepseek-v4-flash`, `deepseek-v4-pro` — are currently
> **cloud-only**, so they cannot replace a local family no matter how much
> better they are.

### Tag case

Ollama **lowercases tags** when it writes a local manifest, so the upstream tag
`glm-4.7-flash:q4_K_M` lands on disk as `glm-4.7-flash:q4_k_m`. All
installed-vs-manifest comparisons are casefolded; without that a manifest model
reports as `MISSING` and an orphan simultaneously, and `prune --remove` would
delete a model the manifest wants.

`prune` also treats **every** host key as wanted, not just the current host's, so
pruning on a Mac can never delete the NVFP4 builds a Linux box pulled.

## OS matrix

| | macOS (Darwin) | Linux (Debian) |
|---|---|---|
| ollama install | Homebrew cask `ollama` (GUI + CLI) | official release tarball (GitHub) extracted into `/usr`, **version-driven** — same block installs *and* upgrades (no `install.sh`) |
| upgrades | `brew upgrade` (cask) | compare installed vs latest tag → `--tags upgrade` re-extracts; optional systemd `ollama-update-check.timer` |
| GPU accel | Metal (built in) | auto-detected: **NVIDIA** CUDA libs bundled (host driver required) · **AMD** `-rocm` overlay (amd64) |
| service | launchd agent `com.ollama.ollama` | systemd unit `ollama.service` (templated) |
| budget basis | unified system RAM | GPU VRAM (else system RAM) |
| model tags | MLX-preferred (`darwin`) | NVFP4 on CUDA (`linux_nvidia`) · GGUF on ROCm/CPU (`linux`) |

### Linux install, GPU & auto-update

The Debian path is Ollama's officially-documented [*Manual install*](https://docs.ollama.com/linux) expressed declaratively — no apt repo exists, so the topic places the release tarball itself, owns the systemd unit, and keeps a matching teardown in `remove.yaml`.

- **Version-driven install/upgrade.** Instead of a `creates:` guard (which never upgrades), the topic resolves a target version, reads the installed `ollama --version`, and re-extracts only when they differ. All Linux tasks carry the `upgrade` tag, so `--tags upgrade` performs a real binary bump.
- **GPU is additive + auto-detected** (a host may have both vendors) via `/sys` PCI vendor IDs:
  - **NVIDIA** (`0x10de`) — CUDA userspace libs ship *inside* the base tarball; only the host **kernel driver** is needed. The topic verifies `nvidia-smi` and **warns** if it's missing. It does **not** install DKMS drivers — that belongs in system/GPU provisioning.
  - **AMD** (`0x1002`) — overlays the separate `ollama-linux-<arch>-rocm.tar.zst` (amd64 only; upstream ships no arm64 ROCm) and adds the service user to `render`/`video`.
- **Periodic update check** (Debian only — macOS upgrades via `brew`). A systemd timer runs [`ollama-update-check`](files/ollama-update-check), comparing the installed binary against the latest upstream tag. Default action is **notify** (journal + a marker at `/var/lib/ollama/update-available`); flip `ollama_update_check_apply=true` to have the timer auto-swap the tarball.

Tunables (`defaults/main.yaml`):

| var | default | meaning |
|---|---|---|
| `ollama_linux_version` | `latest` | `latest` (newest GitHub tag) or a pinned tag like `v0.32.5` |
| `ollama_gpu_nvidia` / `ollama_gpu_amd` | `null` | tri-state: `null` = auto-detect, `true`/`false` = force per host |
| `ollama_update_check_enabled` | `true` | install + enable the update-check timer |
| `ollama_update_check_oncalendar` | `daily` | systemd `OnCalendar=` for the timer |
| `ollama_update_check_apply` | `false` | `false` = notify only · `true` = timer auto-upgrades |

## Who decides what

Ansible reconciles the **system** to the manifest. It does not decide what
belongs in the manifest. Keeping those separate is what lets you change models
without touching provisioning, and re-provision without re-litigating models.

| | who | when |
|---|---|---|
| Which models are declared | **you**, editing `defaults/main.yaml` | whenever |
| Which models exist on a host | ansible → `ollama-models sync` | every provision/upgrade |
| Evidence for the decision | `ollama-usage`, `ollama-bench`, `ollama-models check` | on demand |

Ansible **installs** the analysis tools and schedules exactly one of them; it
never runs a benchmark, never reads a result, and never edits the manifest.

### `ollama-usage` — what actually gets used

Rolls up the `llm` CLI's own log (`responses`: model, tokens, duration) plus
OpenRouter spend. This is how the manifest's context settings stopped being
guesses — 273 logged calls gave p50 ≈ 934 and p90 ≈ 4,591 input tokens, which is
what `ollama_ctx_typical_tokens: 8192` is based on.

```sh
ollama-usage report          # per-model calls, tokens, tok/s + OpenRouter spend
ollama-usage ctx             # input-token percentiles → ctx_typical_tokens
ollama-usage snapshot        # append to history.jsonl  (the scheduled job)
ollama-usage history         # trend across snapshots
```

Only `snapshot` is automated — daily, via launchd on macOS or a systemd *user*
timer on Debian — because a time series has to be sampled to exist. Caveat: it
only sees traffic routed through `llm`. Direct ollama API calls, Claude Code and
`ori` are invisible to it, so treat it as a sample, not a census.

### `ollama-bench` — is the candidate good enough

Rudimentary and unscored by design. It reports cold `load_ms`, prompt and
generation tok/s, and peak resident GB, then saves the full responses so you can
judge quality yourself — the part a benchmark cannot do for you.

```sh
ollama-bench run qwen3.6:27b-mlx gemma4:31b-mlx
ollama-bench run --suite coding <models…>
ollama-bench show --diff a.json b.json
```

Never scheduled: it evicts resident models and takes minutes.

### Swapping a model

1. `ollama-models check --next-gen` — is there a newer generation, and does it
   have local weights? (cloud-only ones are flagged)
2. `ollama pull` the candidate, then `ollama-bench run <incumbent> <candidate>`
3. Read the saved responses; check `peak_gb` against [SIZING.md](SIZING.md)
4. Edit `defaults/main.yaml` — **this is the only step that changes the set**
5. `ollama-models sync`, then `prune` to reclaim the old weights

### Dependency contract

- `topic_requires: [uv]` — the `ollama-models` CLI is a [uv single-file
  script](https://docs.astral.sh/uv/guides/scripts/) (PEP 723 inline deps). **uv
  is installed at the system level** by the astral installer in
  `bootstrap/bootstrap.sh` (not mise-managed — see the mise topic notes), so the
  requirement resolves via the playbook's PATH probe rather than a providing topic.
- The package manager is **not** a hard requirement; it is guarded in-task
  (brew on Darwin, apt/tarball on Debian), since a flat `topic_requires` list
  can't express per-OS dependencies.

### Models download last

Model pulls (hundreds of GB) are **not** run inside the ollama role's tier.
`install.yaml`/`upgrade.yaml` only set up the fast binary + CLI symlink; the
actual `ollama-models sync` (install/provision) and `sync --refresh` (upgrade)
run as a `post_tasks` step in the root `playbook.yaml`, after every tier and
topic finishes — so large downloads never block the rest of provisioning.

### ⚠️ Linux bootstrap assumption

The Linux path assumes the host **already has ansible + mise present** (i.e. a
Linux equivalent of `bootstrap/bootstrap.sh` has run). Building that Linux
bootstrap is out of scope for this topic.

## Links

- [docs](https://docs.ollama.com/) · [macOS reqs](https://docs.ollama.com/macos) · [Linux install](https://docs.ollama.com/linux)
- [git repo](https://github.com/ollama/ollama)
- [brew cask (gui+cli)](https://formulae.brew.sh/cask/ollama-app) · [brew formula (cli-only)](https://formulae.brew.sh/formula/ollama)
- [zsh completion gist](https://gist.github.com/obeone/9313811fd61a7cbb843e0001a4434c58)

## TODO

- Auto-uninstall models dropped from the manifest (reconcile-on-upgrade vs. manual `prune --remove`).
- RedHat family support.
- Resolve dual ansible ownership (brew + mise) — see the mise self-upgrade hazard.
