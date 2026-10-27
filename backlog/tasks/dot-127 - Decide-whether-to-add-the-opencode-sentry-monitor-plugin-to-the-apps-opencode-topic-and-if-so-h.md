---
id: DOT-127
title: Decide whether to add the `opencode-sentry-monitor` plugin to the `apps/opencode`
  topic, and if so h
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Decide whether to add the `opencode-sentry-monitor` plugin to the
  `apps/opencode` topic, and if so how.** Queued 2026-09-16 from the author's
  request, which the agent stopped on. The npm package (MIT, v0.1.7,
  `opencode-sentry-monitor`, by Scott Tolinski) is an OpenCode plugin that
  captures session lifecycle, tool-execution spans, and token usage, and by
  default also tool inputs/outputs and model request/response text
  (`recordInputs`/`recordOutputs` default `true`), then ships them to a Sentry
  project. That is an egress path, and `dotfiles/policy/ethics.yaml` forbids
  egress that is automated end-to-end or bypasses human review
  (`egress.may_be_automated_end_to_end: false`,
  `egress.may_bypass_human_review: false`) while `spec.md` § Policy requires
  every sending tool to consult `policy check` and treat unknown as denied. A
  third-party plugin cannot call the resolver. **Do not add it without the
  author's explicit decision — the telemetry is the whole question.** If
  approved, the shape is an npm entry in `apps/mise/files/config.toml` plus a
  `plugin` entry in `dot_config/opencode/opencode.jsonc.tmpl`, with the egress
  override recorded as an author decision and the recording flags settled.
  Done when the author has answered and the answer is recorded or the plugin
  is wired. [me]
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
