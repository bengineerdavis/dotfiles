# ori

[ori](https://openrouter.ai/blog/announcements/ori-harness) is OpenRouter's CLI
for pointing **agentic coding harnesses** at OpenRouter models. It exists
because getting a first-party-quality experience out of Claude Code (or Codex,
OpenCode, Hermes) against a third-party gateway otherwise means setting a long
list of environment variables by hand. ori detects the model you pick and
applies the right configuration — tool-search enablement, system-prompt
verbosity, and so on.

```sh
ori login          # browser sign-in; skippable — see Authentication
ori claude         # launch Claude Code on an OpenRouter model
ori codex          # …Codex CLI
ori opencode       # …opencode
ori hermes         # …Hermes agent
```

Everything after the flags is passed through to the underlying harness untouched.

## Install

Standalone executable — no bun, node, or python runtime required.

| | |
|---|---|
| Source | `OpenRouterLabs/ori-releases` GitHub releases |
| Asset | `ori-{darwin,linux}-{arm64,x64}` (auto-detected) |
| Destination | `~/.local/bin/ori` (on PATH via `zsh/path.zsh`, no sudo) |
| Verification | SHA256 from the published `SHA256SUMS` |

### Why not the upstream `curl … | bash`?

The upstream one-liner is *only* a downloader: it fetches the same standalone
binary and checks it against the same `SHA256SUMS`. Doing those two steps
natively keeps the install idempotent and change-reporting, and gives it a
precise teardown — the same reasoning applied to the ollama tarball. Nothing is
lost, because there is no other logic in the script.

### Upgrades need no version parsing

`get_url` compares the on-disk binary against the expected SHA256 and only
downloads on a mismatch. A new upstream release changes the checksum, so
`--tags upgrade` swaps the binary; an unchanged release is a genuine no-op
(`changed=0`). Every install task carries the `upgrade` tag because ori is
app-tier but is **not** installed by brew or apt — the system upgrade pass
cannot refresh it, so this topic owns that.

Pin a release with `ori_release_tag: cli-0.4.0-063b32e` instead of `latest`.

## Authentication

`ori login` opens a browser and stores an API key. It is **not** automated here —
interactive credential capture doesn't belong in a provisioning run.

You can skip it entirely: **an inherited `OPENROUTER_API_KEY` beats anything
`login` stores.** Since `llm-openrouter` (managed in `apps/mise/files/config.toml`)
already holds an OpenRouter key, exporting it is often all you need:

```sh
export OPENROUTER_API_KEY="$(llm keys get openrouter)"
```

## Relationship to the rest of the setup

| Layer | Role |
|---|---|
| `apps/ollama` | Local models — free, private, offline, capped at ~24 GB / 4-bit |
| `llm` + `llm-openrouter` (via mise) | Ad-hoc prompting and scripting against remote models |
| `apps/ori` (this) | Drives **full agentic coding harnesses** on remote models |

See [`apps/ollama/MODELS.md`](../ollama/MODELS.md) for which local model to use
for which task, and which remote models are worth escalating to.

## Teardown

`--tags remove` deletes the binary and `~/.config/ori` / `~/.ori`. Credentials
stored in the OS keychain are **not** removed — revoke the key at
<https://openrouter.ai/keys> if you want it fully gone.
