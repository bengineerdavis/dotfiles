---
id: DOT-104
title: Give codex an authenticated provider — the Lore gateway path
status: To Do
created_date: 2026-10-27 02:56
labels:
- planned
priority: high
updated_date: 2026-11-05 02:00
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Give codex an authenticated provider — the Lore gateway path.** Re-cut
  2026-11-05. The author ruled 2026-11-04 that codex routes through the Lore
  gateway; the earlier "Darwin only, chezmoi-managed config.toml" shape is
  retired. The full ruling and its evidence are in
  `backlog/decisions/decision-2`.

The original premise measured false three ways:

1. `apps/loreai/tasks/agents/codex.yaml` already runs `lore setup codex`, which
   writes `openai_base_url = http://127.0.0.1:3207/v1` to
   `~/.codex/config.toml`. Codex has a backend; the task's "no topic provisions
   it" was wrong.
2. That file is owned by three writers — Lore's routing, three git-ai hooks
   with trusted sha256 hashes, and 22 project trust entries. A chezmoi-managed
   `config.toml` would overwrite all of them on every apply.
3. The reported 401 is an authentication defect, not a missing provider: the
   gateway's `/v1/responses` requires a bearer and codex sends none by default.

**Done when** a codex model call returns text through the Lore gateway with no
subscription, using whatever mechanism the ruling permits — a codex profile
(`-p`, layered over the base config) if machine-specific settings are needed,
never chezmoi ownership of `~/.codex/config.toml` itself.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A codex model call returns text through the Lore gateway on this machine, with no OpenAI subscription and no chezmoi ownership of `~/.codex/config.toml`.
- [ ] #2 Whatever supplies the credential does not overwrite Lore's `openai_base_url`, git-ai's three hooks with their trusted hashes, or codex's project trust entries.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Measured 2026-11-05 with `codex-cli 0.161.0`.

Working:

- A provider block with `env_key` makes codex send the OpenRouter key, and the
  gateway accepts it: `base_url = http://127.0.0.1:3207/v1`,
  `env_key = OPENROUTER_API_KEY`, `wire_api = responses`.
- Model IDs must be the **bare** id (`anthropic/claude-haiku-4.5`). The
  `openrouter/`-prefixed form returns `400 not a valid model ID`.
- The gateway answers every codex-shaped request correctly over SSE — plain
  input, `input_text` parts, `instructions`, `tools` with `tool_choice: auto`,
  `store: false`, `reasoning`, `prompt_cache_key` — each returning
  `output_text.delta: "OK"` with `status: completed`.

Not working:

- Codex reports `turn.completed` with `output_tokens: 0` and prints no text.
  The gateway logs `empty completion → client: protocol=openai-responses
  model=anthropic/claude-haiku-4.5 stopReason=end_turn outputTokens=0`. The
  same requests succeed by curl, so the defect is in the codex client's
  handling of the streamed response, not the gateway or the credentials.
- Codex tries the responses websocket first and takes `426 Upgrade Required`
  five times before falling back. `wire_api = "chat"` is rejected outright by
  0.161 ("no longer supported"); the `responses_websockets` and
  `responses_websockets_v2` feature flags are staged `removed`.

Operational note: `lore setup --help` is **not** a help flag — `lore` treats it
as `setup` and reconfigures every app. Use `lore doctor` for read-only
inspection.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `codex exec` returns model text through the gateway on this machine, and `git status` shows no change to `~/.codex/config.toml` ownership.
<!-- DOD:END -->
