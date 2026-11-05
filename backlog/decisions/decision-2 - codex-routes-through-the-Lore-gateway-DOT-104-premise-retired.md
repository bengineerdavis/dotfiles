---
id: decision-2
title: codex routes through the Lore gateway; DOT-104's premise is retired
date: 2026-11-05 02:00
status: accepted
---

## Context

DOT-104 was queued 2026-10-27 with this premise: "`apps/mise` installs
`npm:@openai/codex`, but no topic provisions `~/.codex/config.toml`, so the
binary has no backend and every model call dies with 'Not logged in'/401 (no
codex subscription)." Its done-condition asked for an `apps/codex` topic
shipping a chezmoi-managed `config.toml` with a `model_providers` block on the
OpenRouter key.

Every part of that premise measured false on 2026-11-02/04:

1. **A topic does provision the file.** `apps/loreai/tasks/agents/codex.yaml`
   runs `lore setup codex`, which writes
   `openai_base_url = "http://127.0.0.1:3207/v1"` and
   `model_auto_compact_token_limit = 999999999` to `~/.codex/config.toml`.
   Codex has a backend.
2. **The file is owned by three writers, not one.** It carries Lore's
   `openai_base_url`, three git-ai hooks with trusted sha256 hashes, and 22
   project trust entries. A chezmoi-managed `config.toml` would clobber all of
   it on every apply — the exact failure decision-1 §3 calls a same-purpose
   duplicate, arrived at from the other direction.
3. **The 401 is an authentication defect, not a missing provider.** Codex sends
   no credential; the gateway's `/v1/responses` requires one. Measured: `POST`
   without a bearer → `401 "No cookie auth credentials found"`. The default
   `openai` provider inherits the user's OpenAI key, which OpenRouter rejects
   (`Incorrect API key provided: sk-or-v1…`, forwarded to platform.openai.com).

The author ruled on 2026-11-04: **codex routes through the Lore gateway.** The
alternative — pointing codex at OpenRouter directly — would put a second
model-routing path in the fleet for one client, and the gateway is already the
single upstream for every other agent here.

## Decision

Codex uses the Lore gateway as its backend. The author ruled (2026-11-04)
against a direct-to-OpenRouter path.

Consequences that follow mechanically:

- **No `apps/codex` topic owns `~/.codex/config.toml`.** The file stays
  tool-owned: `lore setup codex` writes the routing, git-ai writes its hooks,
  codex itself writes project trust. Chezmoi does not manage it.
- **DOT-104's done-condition is void as written.** It asked for a
  chezmoi-managed config.toml, which is precisely what must not happen.
- **The remaining work is the gateway auth path**, tracked separately. It
  overlaps the `loreai-key-capture` branch (an env-capture defect: `llm keys
  get openrouter` captured a PyMuPDF notice on stdout, producing a 98-byte key).

## Measured state (2026-11-05, `codex-cli 0.161.0`)

Auth is **solvable with a provider block**; an empty completion remains.

Working:

- A provider block with `env_key` makes codex send the OpenRouter key, and the
  gateway accepts it. `base_url = http://127.0.0.1:3207/v1`,
  `env_key = OPENROUTER_API_KEY`, `wire_api = responses`.
- The gateway itself is healthy. Every codex-shaped request answered correctly
  over SSE — plain input, `input_text` parts, `instructions`, `tools` with
  `tool_choice: auto`, `store: false`, `reasoning`, `prompt_cache_key` — all
  returned `output_text.delta: "OK"` with `status: completed`.
- Model IDs must be the **bare** id (`anthropic/claude-haiku-4.5`); the
  `openrouter/`-prefixed form returns `400 not a valid model ID`.

Not working:

- Codex reports `turn.completed` with `output_tokens: 0` and prints no text.
  The gateway log shows `empty completion → client: protocol=openai-responses
  model=anthropic/claude-haiku-4.5 stopReason=end_turn outputTokens=0`. Since
  identical requests succeed by curl, the defect is in the codex client's
  handling of the streamed response, not in the gateway or the credentials.
- Codex attempts the responses **websocket** first (`426 Upgrade Required`, 5
  retries) before falling back to HTTP. `wire_api = "chat"` is rejected
  outright by 0.161 (`no longer supported`); the `responses_websockets` and
  `responses_websockets_v2` feature flags are staged `removed`.

## Consequences

- DOT-104 is re-cut from an implementation task to record this ruling and the
  measured state; the auth work is routed to the LoreAI topic, where the
  gateway belongs.
- No chezmoi source takes ownership of `~/.codex/config.toml`. If a future
  need for machine-specific codex settings appears, codex's profile layering
  (`-p/--profile`, `$CODEX_HOME/<name>.config.toml` layered over the base
  config) is the seam — a profile file can be chezmoi-managed without
  competing with Lore or git-ai for the base file.
- The single-config rule (decision-1 §3) is why this decision exists at all:
  the original task's shape would have created exactly the duplicate the rule
  forbids.
