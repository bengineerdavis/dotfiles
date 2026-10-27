---
id: TASK-142
title: Extract the model benchmarking and scouting tools into their own repository
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Extract the model benchmarking and scouting tools into their own repository.**
  Near-future and deliberate, not urgent — recorded now so it does not happen by
  accident. `bin/model-bench` is 1357 lines and `bin/model-scout` is 379, plus
  `apps/ollama/files/ollama-bench` and `ollama-evals`; that is a model
  evaluation toolkit living inside a machine-provisioning repo. It is also the
  clearest case of the `AGENTS.md` ladder: AI work belongs outside this repo,
  and benchmarking models is not configuring a machine. Same destination shape
  as `topical` — its own repo, installed back here as a normal tool by a thin
  topic, rather than vendored. Two things to settle before moving: the tools are
  referenced by name in `.claude/settings.local.json` allowlists and in launchd
  labels (`com.ollama-usage.snapshot`), so this shares the audit in A10 above;
  and `ollama-evals`/`ollama-bench` are topic-owned while the `bin/` pair are
  not, so the split is not along one clean line today. Done when benchmarking
  lives in its own repo, this repo installs it like any other tool, and nothing
  here imports it.
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
