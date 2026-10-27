---
id: TASK-205
title: Generalize the golden-transcript pattern for `llm_judge` tests, instead of
  a VCR-style HTTP recorder
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Generalize the golden-transcript pattern for `llm_judge` tests, instead
  of a VCR-style HTTP recorder.** Researched 2026-09-22, prompted by
  `pytest-recording` (kiwicom, real and mature — 615★, MIT): it doesn't fit
  here. VCR.py patches HTTP libraries inside the *test process*; this repo's
  `llm_judge` tests call models via `subprocess.run` (`pii-redactor` → the
  real `llm` CLI, a grandchild process) — the network call never happens
  where an in-process recorder is watching. The herdr work already proved
  the right-shaped mechanism once: "a golden transcript against the real
  binary caught the `letta (experimental)` wire variant" no library would
  have shown. Generalize that into a convention — record subprocess stdout
  to a fixture file once, replay from file by default, `--record` flag (or
  `llm_judge`-style marker) re-runs against the real model to refresh it —
  rather than adopting a tool that architecturally cannot reach the calls.
  Also verified the same session: `pytest-agentkit`, `pytest-agentprobe`,
  `pytest-agent-eval`, `pytest-agent-health` — not adopted now, watch-listed
  instead (§ Planned, "Watch the pytest-agent-* ecosystem").
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
