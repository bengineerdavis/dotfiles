---
id: DOT-58
title: Consolidate the governance docs — PRD as the constitution, spec as the derived
  statutes, conventions
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Consolidate the governance docs — PRD as the constitution, spec as the
  derived statutes, conventions as the how-to.** [#2, was #1 until the author
  reordered the multiagent work ahead of it 2026-09-20] Decided with the author
  2026-09-16: PRD states each requirement once; spec derives its testable
  SHALL/BDD form and cites the principle back; AGENTS-referenced convention
  docs explain how to comply. The four docs are currently peers with no stated
  precedence, and PRD has smuggled constraints (the provision-vs-logic rule,
  the verification governor) that belong in spec — the drift behind the
  changelog "discipline gap" (d1f10ff). Items, in order: (1) derivation-graph
  inventory — map every spec.md behavior to its PRD.md principle and back,
  marking orphans and unstatuted principles; (2) write the precedence rule into
  the docs; (3) prune the drift — move smuggled statutes into spec with
  citations; (4) retire the stale root docs/ tree (edit dotfiles/docs/ only);
  (5) review TASKS.md § Now/Planned against the consolidated requirements.
  Done when every spec behavior cites a PRD principle, PRD holds no testable
  statutes, one maintained copy of each doc exists, and the open task list has
  been re-reviewed. [me]
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
