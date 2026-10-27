---
id: DOT-118
title: Add an ollama model-health check for every model project tooling invokes
status: To Do
created_date: 2026-10-27 02:56
labels:
- planned
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Add an ollama model-health check for every model project tooling invokes.**
  Author queued 2026-09-22, deferred — lower priority, no action taken in the
  shift-left study. Trigger: the shift-left fusion council found every MLX
  model on ollama fails at call time (`mlx runner exited unexpectedly`,
  exit status 2/500 — verified 2026-09-22 on qwen3.6:35b-mlx and
  gemma4:12b-mlx; GGUF olmo-3.1:32b works), and `tests/pii_redactor/conftest.py:29`
  requests `qwen3.5:4b-mlx-bf16` by exact tag, failing into test failure when
  absent. Principle from the author: any model a tool or test calls must be
  verified to exist and respond — model availability becomes a tested
  property, not an assumption. Done when a check (test or preflight) confirms
  each invoked model id exists in `ollama list` and answers a call, and
  tooling that depends on a missing/broken model skips-with-reason instead of
  failing. [me]
  *Evidence 2026-09-22 evening:* a restart of `com.ollama.server` fixed it —
  `gemma4:12b-mlx` and `qwen3.8:27b-mlx` answered afterwards. The cause is not
  established. The server process had run since 2026-09-12 on 0.33.3, and brew
  installed 0.34.3 at 17:52 PDT without restarting it, so by evening client and
  server disagreed. But the 09:32 failure predates that upgrade, so the mismatch
  cannot explain it; a fresh process and a new version arrived together and
  this evidence cannot separate them. The upgrade path not restarting the
  server is its own defect regardless.
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
