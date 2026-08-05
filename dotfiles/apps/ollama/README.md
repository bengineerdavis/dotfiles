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

- **add a model** → copy a line under its family; set the `darwin`/`linux` tags + `size_gb`
- **add a family** → add a new `family-name:` key with a list of members
- **drop a model** → delete/comment its line. Upgrades stop refreshing it, but
  already-pulled weights are **not** auto-deleted (see `prune` below)

### Commands

```sh
ollama-models status              # installed / missing / skipped-oversized, per family
ollama-models sync                # pull manifest models that are missing (first-run behavior)
ollama-models sync --refresh      # update to latest — re-pulls only models whose
                                  #   upstream manifest digest changed (unchanged = skipped)
ollama-models sync --dry-run      # print what would be pulled, pull nothing
ollama-models check               # diff each family's upstream tags vs the manifest;
                                  #   flags NEW/unknown precision keywords (future formats)
ollama-models check --next-gen    # additionally probe for newer family generations
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

## Precision & sizing rules

Each member's tag is chosen by these rules (Mac prefers MLX; GGUF-only families
fall back to q-quants, which run fine on Metal):

| Model size | Precision | macOS tag | Linux tag |
|---|---|---|---|
| small (≤4B params) | full | `-mlx-bf16` / `-bf16` | `-bf16` / `-fp16` |
| large (>4B) | fp8 if it fits budget, else fp4 floor (never below fp4) | `-mxfp8` / `-mlx` / `-nvfp4` | `-mxfp8` / `-nvfp4` / `-q*_K_M` |
| embeddings | full precision, identical on both OSes | `-bf16` / `-fp16` | `-bf16` / `-fp16` |

**Budget gating:** `size_gb` on each entry is checked against a runtime budget of
`total − ollama_ram_reserve_pct` (default 33%). Anything larger is skipped with a
log line, so the same manifest works on a 16 GB laptop and a 128 GB box. On macOS
the basis is unified system RAM; on Linux with an NVIDIA GPU it is **VRAM**
(`nvidia-smi`), falling back to system RAM for CPU inference.

## OS matrix

| | macOS (Darwin) | Linux (Debian) |
|---|---|---|
| ollama install | Homebrew cask `ollama` (GUI + CLI) | official release tarball (GitHub) extracted into `/usr`, **version-driven** — same block installs *and* upgrades (no `install.sh`) |
| upgrades | `brew upgrade` (cask) | compare installed vs latest tag → `--tags upgrade` re-extracts; optional systemd `ollama-update-check.timer` |
| GPU accel | Metal (built in) | auto-detected: **NVIDIA** CUDA libs bundled (host driver required) · **AMD** `-rocm` overlay (amd64) |
| service | launchd agent `com.ollama.ollama` | systemd unit `ollama.service` (templated) |
| budget basis | unified system RAM | GPU VRAM (else system RAM) |
| model tags | MLX-preferred | nvfp4 / GGUF |

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
