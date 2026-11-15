---
id: DOT-361
title: Reconcile ask-matt's issue-tracker contract with the backlog store
status: To Do
created_date: 2026-11-15 20:21
priority: high
dependencies:
- DOT-360
updated_date: 2026-11-15 20:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The ask-matt skill family routes its flows through an issue tracker, and
`setup-matt-pocock-skills` ships three adapters — github, gitlab and local —
with no backlog one. The local adapter specifies `.scratch/<feature>/spec.md`,
issues at `.scratch/<feature>/issues/NN-slug.md`, a `Status:` line for triage
state and a `Blocked by: NN, NN` line for edges. This repo stores tasks at
`backlog/tasks/dot-N - Title.md` with frontmatter `status`, `dependencies`,
`priority` and marker-delimited AC blocks. A session reading both AGENTS.md
and an ask-matt flow sees two tracker conventions and no rule for which
applies, which is the likeliest reason the store's own instructions were never
adopted here (DOT-360).

Ship:

- A backlog adapter for the ask-matt tracker contract, mapping each operation
  the flows call — publish, fetch, claim, resolve, frontier, blocking edges —
  onto backlog-py verbs
- The mapping for wayfinding operations, since `/wayfinder` drives map and
  child tickets through the same contract
- A statement of which tracker this repo uses, so `.scratch/` is never created
  alongside `backlog/`
- The adapter carried into the template so stamped projects inherit one
  tracker, not two

Constraints:

- Read each skill's SKILL.md before asserting what it does; the ask-matt
  summaries are orientation only, by that skill's own instruction
- Adapter work is a mapping, not a fork of the skills
- `/to-tickets` output is already agent-ready and must not be routed through
  `/triage`, which is for issues the author did not write
- Any capability claim about a skill or CLI is verified against the artifact
  before the design depends on it
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A backlog adapter exists mapping publish, fetch, claim, resolve, frontier and blocking edges onto backlog-py verbs
- [ ] #2 Wayfinding map and child-ticket operations are mapped onto the backlog store
- [ ] #3 The repo states which tracker it uses, and no .scratch/ tracker is created alongside backlog/
- [ ] #4 The adapter is carried into agentic-project-template so stamped projects inherit one tracker
- [ ] #5 Each mapped claim is verified against the skill's SKILL.md or the CLI, not recalled
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
