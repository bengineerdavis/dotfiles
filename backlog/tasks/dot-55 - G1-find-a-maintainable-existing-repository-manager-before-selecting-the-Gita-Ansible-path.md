---
id: DOT-55
title: G1 — find a maintainable existing repository manager before selecting the Gita/Ansible
  path
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**G1 — find a maintainable existing repository manager before selecting
  the Gita/Ansible path.** After G0, alongside BK1 and the existing
  second-machine inventory, compare established multi-repository tools and
  Ansible modules, roles and collections against the approved workflow.
  Evaluate human-facing workflow and interface simplicity, current and
  usable documentation, and fit to the handoff's machine selection, GitHub
  discovery, remote matching, fetch-safe sync, per-repository verdicts,
  non-aborting report, and freshness requirements. Include the preliminary
  Gita/ghorg/Ansible research in
  `dotfiles/docs/research/repo-manager/GITA-RESEARCH.md`, but widen
  its candidate set before recommending. Follow
  `dotfiles/docs/TOPIC-RECIPES.md`'s docs-and-Galaxy-first rule. If no
  existing tool meets the need, specify the smallest Ansible-module/role
  composition that could, what it still cannot do, and any contract or
  ownership decisions needed; do not design a bespoke engine or implement
  it here. Done when a sourced comparison ranks the existing options,
  records rejections, recommends a path that minimizes customer-maintained
  logic, and the author records the choice. The result hands the discovery
  and sync mechanisms to G2/G3/G4/G7. The expanded report is prepared at
  `dotfiles/docs/research/repo-manager/GITA-RESEARCH.md`. The author
  accepted task-level Ansible orchestration as the fallback on 2026-09-24,
  and asked for the complete workflow and candidate links before choosing
  the final tool split. No tool has been adopted yet. [agent: gita-plan / OpenCode]
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
