---
id: DOT-283
title: Build the slow loop that migrates topics onto a CLI secrets manager
status: To Do
created_date: 2026-11-03 04:13
labels:
- planned
- design
- ansible
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The author asked (2026-11-02) for a slow loop that incrementally moves topics off ad-hoc secret sources and onto a CLI secrets manager (Bitwarden or 1Password), rather than one big migration. Today the payload has three delivery routes and no owner for choosing between them.

Measured 2026-11-02 on this checkout:

- Only two topics read a secret themselves. `home/dotfiles/apps/loreai/templates/loreai-env.zsh.j2:39` captures the OpenRouter key with `llm keys get openrouter` (with a commented `op read` line above it, and the comment "a secrets manager is the intended home; \`llm keys\` is the fallback, NOT the source of truth"), and `home/dotfiles/apps/ollama/files/executable_ollama-evals` reads the same key the same way. `home/dotfiles/apps/loreai/tasks/prompts.yaml` only probes reachability.
- The fragile route is not hypothetical. `llm keys get openrouter` writes PyMuPDF's deprecation notice to STDOUT, so `2>/dev/null` does not filter it and the captured value became "warning: …\nsk-or-v1-…" (98 bytes instead of 73). The gateway held that poisoned value and every background worker failed with `Headers.append: … is an invalid header value` for 43 minutes. Fixed on the machine 2026-11-02 by `tail -n1`, but the template still ships the unfiltered form.
- A shared helper already exists and is under-used. `home/dotfiles/roles/secrets-session/` (README + bitwarden.yaml + onepassword.yaml + tests) produces in-memory session facts, never writing secrets to disk. Two topics use it: `apps/deb-get` (`debget_secrets_manager: bitwarden` default) and `apps/uv` (`uv_secrets_manager: onepassword`, reading `op://Private/uv-private-index/{url,username,password}`). No other topic calls it.
- Both CLIs are already provisioned as topics (`apps/bitwarden`, `apps/1password`), installed via mise here. On this machine `bw status` reports `locked` and `op account list` is empty, so neither vault is signed in — a migration loop must fail closed and say so, not silently fall back to `llm keys`.
- `llm`'s key store (`~/.config/io.datasette.llm/keys.json`) is plaintext JSON with three keys and is not chezmoi-managed or ignored by any rule found; it is a second, unrecorded credential store.

The loop this task builds is the mechanism, not the conversion: a periodic, resumable pass that takes one topic at a time from an ad-hoc source to a named vault reference, proves the topic still works, and records the evidence — so the migration can stop anywhere and resume, and a half-migrated fleet is never worse than today. Per AGENTS.md the mechanism is configuration plus a check, not a new tool: if the pass needs bespoke code beyond the existing role seam, that is a surface-and-ask, not a build.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 docs/ names the secret-delivery contract — which route a topic must use, who owns the choice, and how a topic declares a vault reference instead of reading a key itself
- [ ] #2 The loop is resumable and incremental: one topic per iteration, with recorded per-topic state so a half-migrated fleet is no worse than today
- [ ] #3 Each iteration proves the topic still works after migration (its existing tests plus a live check where the topic has one); a failing vault session fails closed with a stated fix, never a silent fallback to `llm keys get`
- [ ] #4 A check reports every remaining ad-hoc secret read in the payload, so the migration's progress is measured rather than asserted
- [ ] #5 The loreai template's key capture is fixed as the first iteration, including a test whose `llm` stub prints a decoy line before the key so the unfiltered form cannot return
- [ ] #6 The loop's cadence and stopping condition are recorded, and the per-machine vault choice (Bitwarden vs 1Password) is stated rather than inferred
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 No topic reads a secret by shelling out to `llm keys get` unless docs/ records why that topic is deliberately exempt
- [ ] #2 The AC4 check is green against the converted set, and its red state has been seen against a deliberately reintroduced `llm keys get`
<!-- DOD:END -->
