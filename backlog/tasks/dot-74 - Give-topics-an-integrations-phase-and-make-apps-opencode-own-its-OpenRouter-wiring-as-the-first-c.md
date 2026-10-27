---
id: DOT-74
title: Give topics an integrations phase, and make `apps/opencode` own its OpenRouter
  wiring as the first c
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Give topics an integrations phase, and make `apps/opencode` own its
  OpenRouter wiring as the first case.** `dot_config/opencode/opencode.jsonc`
  already points `model` at `openrouter/z-ai/glm-5.3-flash` and `small_model`
  at `ollama/qwen3:8b`, while `apps/opencode` declares `topic_requires:
  [homebrew, node]` and checks neither provider — auth is a manual `opencode
  auth login` that the README leaves to the reader. A freshly provisioned
  machine therefore deploys a config whose default model cannot answer, and
  nothing in the run says so. The convention to write into `docs/TOPICS.md`:
  when a tool needs a provider or CLI at **runtime** rather than to install
  (openrouter, ollama), the tool's own topic decides on it and acts — it checks
  whether the dependency is reachable and owns the logic to add the integration
  and to take it back out, rather than delegating either to the provider's
  topic. Integrations stay separate from installation: they run only **after**
  the tool is installed, and are skipped and reported — never failed — when the
  tool is absent or the user declined it. That ordering is why this is a phase
  of its own and not more `install.yaml`. Go through **`ori`** rather than
  hand-rolling provider config: `ori opencode` is OpenRouter's own supported
  path for pointing opencode at its models, and `apps/ori` already declares
  `topic_provides: [ori]`, so the integration can require it through the
  existing dependency graph instead of a PATH probe. The two failure modes are
  deliberately not the same: a missing or declined **opencode** is a skip, while
  a missing `ori`, or an `ori` that runs and cannot complete the integration, is
  **raised** — the run fails with the named fix, or the agent surfaces it, rather
  than leaving a half-wired provider behind. Mind the auth constraint the ori
  README already records: `ori login` is interactive and deliberately not
  automated, and an inherited `OPENROUTER_API_KEY` beats whatever it stores — so
  the integration must work from that key and fail loudly, naming it, when
  neither is present. Done when `apps/opencode` wires OpenRouter through `ori`,
  confirms it with a check whose pass/fail the run reports (`opencode auth list`
  at minimum, a one-token completion if that proves too weak), skips cleanly
  where opencode was never installed, raises rather than skips when `ori` is
  absent or fails, takes the integration back out under `--tags remove`, and
  `docs/TOPICS.md` states the convention so the next tool follows it without
  re-deciding.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
