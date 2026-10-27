---
id: DOT-80
title: Extend `dotfiles-triage` from naming a cause to proposing the fix, as a guarded
  PR
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Extend `dotfiles-triage` from naming a cause to proposing the fix, as a
  guarded PR.** Build on the public, vendor-neutral prior art, not on Sentry's
  Seer: `getsentry/seer` is `visibility: internal` (confirmed 2026-09-12 via
  `gh api repos/getsentry/seer`), so it is not a source this repo may read from,
  and nothing about the pattern requires it. The documented loop is older and
  plainer than any product — fail, halt, investigate, produce an RCA, open a PR
  carrying the RCA as its description, let a human merge. Target CARM L3
  (diagnose + propose) and stop there: **never self-apply**, which is the same
  never-auto-repair rule `roles/guards/` already follows and for the same reason.
  Every guard in `roles/guards/` is a detector that already knows its own fix
  text, so they are the natural first inputs. Done when a deliberately broken
  topic run produces a branch and a PR whose description is the RCA, and no run
  can mutate the machine without a human merging.
  **Three controls make this safe enough to run on a work machine, and they are
  cheap.** (1) A source-provenance note per design decision, naming the public
  page it came from — the tractable half of clean-room, minus the pretence that
  one person can staff two teams. (2) An explicit read-exclusion list, not one
  path: `~/code/work/sentry/` (a Seer clone sits at
  `~/code/work/sentry/what-would-kobby-do/seer`) **and** the unlicensed internal
  skills now sitting in the user-global skill path. "Do not consult it" has to be
  a rule the tool enforces, not an intention. (3) The existing fail-closed
  resolver (`bin/policy`, ethics > company > personal) gates anything that
  matters off this machine: remote model calls, log bodies, reading outside an
  allowlist. Nothing new is invented for safety; it is provenance plus the gate
  already built and tested. [me]
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
