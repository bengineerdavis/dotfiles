# loreai

[Lore.AI](https://withlore.ai) is a persistent-memory gateway for AI coding
agents. Agents route through it — per-launch via `lore run`, or persistently
via `lore setup <app>` — and it records sessions, distills them in the
background, and injects curated knowledge into later ones. The memory
database stays on the machine (`~/.local/share/lore/lore.db`).

## Install

Standalone executable, checksum-verified — no node, bun, or python runtime.

| | |
|---|---|
| Source | `BYK/loreai` GitHub releases |
| Asset | `lore-{darwin,linux}-{arm64,x64}` (auto-detected) |
| Destination | `~/.local/bin/lore` (on PATH via `files/zsh/path.zsh`, no sudo) |
| Verification | SHA256 from the release's `lore-checksums.txt` |

Why not the hosted `curl … | bash`? It is only a downloader plus a
shell-profile edit. Doing the download natively keeps it idempotent and
removable (the `apps/ori` reasoning); the profile edit is this topic's
`files/zsh/path.zsh` instead. The install tasks carry `[install, upgrade]` —
no system role reaches a GitHub-release binary, so this topic owns upgrades
(`get_url` re-downloads only on checksum change). Pin a release with
`loreai_release_tag: 0.41.0` instead of `latest`.

## First install asks; later installs don't

The first install prompts — **before touching anything** — for two answers
saved per machine to `~/.config/loreai/env.zsh` (sourced by
`files/zsh/env.zsh`):

1. **Telemetry** — production builds send privacy-filtered operational
   telemetry to Sentry by default
   ([details](https://withlore.ai/docs/install/#operational-telemetry)).
2. **Worker inference** — where background workers run: `openrouter`
   (default when a key is detectable), `local` (ollama, when found), or
   `none` (workers follow the session provider).

Delete the file and re-run to re-answer. Non-interactive runs pass
`-e loreai_telemetry=0|1 -e loreai_inference=openrouter|local|none`
(optionally `-e loreai_worker_model=<provider/model>`) or fail fast before
changing anything.

## Agent extensions

Each supported agent is an extension, configured only when detected (a CLI
on PATH; codex also counts an existing `~/.codex/config.toml`):

| Agent | Mechanism | What it writes |
|---|---|---|
| claude-code | `lore setup claude-code` | `~/.claude/settings.json` |
| codex | `lore setup codex` | `~/.codex/config.toml` |
| pi | `lore setup pi` | `~/.pi/agent/models.json` |
| hermes | `lore setup hermes` | `~/.hermes/.env` |
| opencode | **chezmoi plugin fragment** | `~/.config/opencode/opencode.jsonc` |

opencode is the exception because chezmoi owns its config here — and when
both `opencode.json` and `.jsonc` exist the `.jsonc` wins, so
`lore setup opencode`'s writes would be shadowed. The template
(`dot_config/opencode/opencode.jsonc.tmpl`) includes this topic's
`files/opencode/lore-plugin.jsonc` behind a stat guard; opencode
auto-installs the plugin on first run, and the plugin disables compaction
and routes sessions through the gateway itself. Removing the topic
directory removes the key on the next `chezmoi apply`.

Note for the persistent setups (claude-code, codex, …): the agent's
provider now points at the gateway, so the gateway must be running —
`lore start`, or keep launching via `lore run` (which manages the gateway
per-invocation and needs no setup at all).

## Independence and prerequisites

The topic installs **independently of every other topic**:
`topic_requires: []` — the binary is standalone and needs no package
manager, so the parent playbook's dependency resolver asks for nothing.
The one external tool it shells out to (`gunzip`) is probed up front with
the fix named. The `llm` key probe degrades to "no OpenRouter key" when
`llm` is absent; choosing `openrouter` without a resolvable key earns a
loud warning at install, not a silent worker failure later.

**Agents may arrive in any order, or never.** Detection re-runs on every
install: an agent installed later is configured on the next run of the
topic. When **no agent is detected**, the install still succeeds — the
binary and the per-machine answers land — and the run reports each
undetected agent with the fix ("install one and re-run the topic, or run
`lore setup <app>`"). Nothing is half-configured and nothing fails.

## Worker model: the decision record

Lore has **one** worker model for all background pipelines (distillation,
curation, query expansion) — verified in the BYK/loreai source
(`worker-model.ts`: no per-pipeline knob; `LORE_WORKER_MODEL` is the
top-priority override; cross-provider workers are explicitly supported via
`LORE_WORKER_API_KEY`/`LORE_WORKER_UPSTREAM`, and `openrouter` is a
first-class provider whose auth resolves from `OPENROUTER_API_KEY`). One
knob means the pick must clear the hardest bar: **curation**, the
judgment task (structured write authority over the knowledge base).
Distillation and query expansion tolerate far weaker models, but nothing
per-pipeline exists to route them to.

Evidence behind the default (`openrouter/z-ai/glm-5.3-flash`):

- **Lore's own default encodes the same tiering rule**: workers drop to
  sonnet-4-6 when the session model is expensive — a capable mid-tier, not
  a nano-class model ("equivalent-quality distillations at lower cost",
  `packages/core/src/worker-model.ts`).
- **Memory-system construction pipelines with hard output contracts fail
  on tiny models** (arXiv 2606.06448: MIRIX fails at Qwen3-1.7B; systems
  without contracts degrade smoothly). Lore's curator writes structured
  entries → treated as a hard-contract pipeline → no nano-class pick.
- **Lore's guide floors local curation at 32B+ Q4**; the local tier below
  is all 32B-class house-measured tags (`apps/ollama/MODELS.md`).
- glm-5.3-flash is this fleet's existing opencode default model, so worker
  traffic crosses no new trust boundary. `anthropic/claude-haiku-5.5` is
  the first fallback for keeping workers inside the Anthropic boundary
  Claude Code sessions already use.

Rejected: `openai/gpt-5-nano` and `google/gemini-2.5-flash-lite`
(sub-curation-bar class per the hard-contract evidence);
`deepseek/deepseek-v4-pro` (not the flash line the author asked for;
`deepseek-v4.1-flash` is recorded instead). The full reviewed-alternate
list lives in `defaults/main.yaml` (`loreai_worker_model_candidates`) and
lands in the machine env file as comments — switching is a one-line edit.
Prices are volatile; re-check the catalog before switching. These are
**starting candidates, not measured endorsements** (spec § Models) —
`bin/model-bench` is the way to measure them on this machine later.

## Existing conversations

Report-only at install (author ruling 2026-10-21): the install prints what
`lore import --dry-run` would pick up for the checkout it runs from, and
names the per-project command. `lore import` is idempotent and
per-project; `lore run` offers a one-time auto-import per newly detected
agent. Provisioning never spends curator tokens on your behalf.

## Teardown

`--tags remove` runs `lore setup undo <app>` per agent (restores only what
setup changed), deletes the binary, the per-machine env file, and
`~/.cache/lore`. It **preserves** `~/.local/share/lore` (the database) and
`~/.lore` (channel/update metadata) — printed for manual review, the same
default `lore uninstall` makes. The opencode plugin key disappears from the
deployed config on the next `chezmoi apply` after the topic is removed.
