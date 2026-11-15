---
id: DOT-359
title: Template AGENTS.md so agents behave correctly before, during, and after stamping
status: To Do
created_date: 2026-11-15 20:21
labels:
- now
priority: high
dependencies:
- DOT-360
- DOT-361
updated_date: 2026-11-15 20:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
AGENTS.md is assembled per project by hand today. agentic-project-template
carries fragments (agents-md-section.md, agents-md-backlog-section.md,
fragments/tools/*/agents.md for eleven tools) but no contract for how they
compose, what a stamped AGENTS.md must contain, or how a project's own rules
survive a re-stamp. The result is visible in this repo: 1,063 lines, a tracker
section that does not match the store's own instructions (DOT-360), and a
second tracker convention arriving through the skills (DOT-361). Agents need
correct instructions at three moments — before stamping (what the template
expects of the host), during (what gets written), and after (what a re-stamp
may rewrite).

Ship:

- A contract for the stamped AGENTS.md: required sections, their order, and
  which are tool-owned versus project-owned
- Deterministic stamping of tool-owned sections from fragments, so a re-stamp
  reproduces them rather than appending
- A written rule for the three moments: host prerequisites checked before,
  sections written during, and managed-block boundaries honoured after
- The feedback from this session folded in as the first content: commit
  scoping under a shared index, one writer per worktree, and the tool-surface
  rule

Constraints:

- Managed blocks are rewritten, project prose never is — the
  CODING_STANDARDS_HEADER contract (agentic-project-template, 2026-11-09)
- Composition merges additively and idempotently; stamping twice equals
  stamping once
- Layering extends exactly one layer; an everywhere-feature is declined as a
  grab-bag
- Writing targets agents, per the writing-for-agents reference the retro and
  ask-matt skills both cite
- Sequenced behind DOT-360 and DOT-361: the tracker contradiction is settled
  before the file that carries it is templated
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A contract names the stamped AGENTS.md sections, their order, and tool-owned versus project-owned
- [ ] #2 Tool-owned sections stamp deterministically from fragments; stamping twice equals stamping once
- [ ] #3 Host prerequisites are checked before stamping and reported when unmet
- [ ] #4 A re-stamp rewrites managed blocks only and leaves project prose untouched, proven by a stamp test
- [ ] #5 This session's lessons are present: commit scoping under a shared index, one writer per worktree, verify the tool surface
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
