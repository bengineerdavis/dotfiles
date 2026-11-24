---
id: DOT-358
title: Make the post-mortem and remediation flow a callable skill with self-detected
  prerequisites
status: To Do
references:
- backlog/decisions/decision-3 - VM-verify-config-and-symlink-deployments-before-apply-merge-and-PR-gates.md
created_date: 2026-11-15 06:41
dependencies:
- DOT-275
- DOT-357
updated_date: 2026-11-15 06:42
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The post-mortem flow exists as convention, not as something an agent can call:
classify a failure, capture it as a decision record, link remediation tasks
through `references:`, retire the rule when they land. A session either knows
the convention or reinvents it. The author wants it callable directly or
indirectly by agents and sessions, and eventually shareable beyond this repo.

A skill is a refactor of a flow that works, so this lands after its two halves
are settled: DOT-275 defines what counts as an incident (capture), DOT-357
defines resolution and thinning (retirement). Writing the skill first would
encode a flow nobody has run end to end.

Ship:

- A spec-first skill in ai-prompt-library following the `backlog-task`
  precedent (SKILL.md + spec.md, skillet-authored, evals)
- A description that routes: when to classify-and-capture, and the stores and
  repo shapes it declines
- Prerequisite self-detection, answered from files rather than new state:
  `backlog/config.yml` and `backlog-py` present; `backlog/decisions/` exists;
  `references:` available in task frontmatter; DOT-275 Done — `To Do` means
  stop and say why
- A portable procedure layer (classify, capture as ADR, link remediation,
  retire on resolution) kept separate from this repo's bindings

Constraints:

- Author spec-first through skillet; the rendered SKILL.md is generated, never
  hand-edited
- Separate procedure from bindings in the spec from the start: `backlog/decisions/`,
  the `references:` field and AGENTS.md as the rule surface are local conventions,
  and hard-coding them makes the skill fail its own self-detection elsewhere
- Extend the lifecycle gap rather than overlapping `backlog-task`, which covers
  record creation only and excludes closing, claiming and reassignment
- Refuse rather than guess: an unsettled prerequisite stops the run with the
  reason, per the prime directive
- No new backlog record type — incident is a decision subtype

Blocked on DOT-275 (incident definition) and DOT-357 (retirement lifecycle).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A spec-first skill exists in ai-prompt-library with SKILL.md, spec.md and evals, following the backlog-task precedent
- [ ] #2 The description routes on when to classify-and-capture and names the stores and repo shapes it declines
- [ ] #3 Prerequisites are detected from files: backlog config and CLI present, backlog/decisions/ exists, references: available, DOT-275 Done
- [ ] #4 An unsettled prerequisite stops the run and states the reason instead of guessing
- [ ] #5 The spec separates the portable procedure from this repo's bindings
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
