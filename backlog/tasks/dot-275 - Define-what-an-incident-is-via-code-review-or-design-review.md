---
id: DOT-275
title: Define what an incident is via code review or design review
status: To Do
created_date: 2026-10-29 23:38
references:
- backlog/decisions/decision-1 - VM-verify-config-and-symlink-deployments-before-apply-merge-and-PR-gates.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per decision-1 amendment (2026-10-29): before incidents can be captured mechanically as backlog post-mortems, the repo needs an agreed definition of what counts as one. The author requires a code review or design review session to define the boundary. Candidate axes to settle: severity threshold (destabilized user-level usage vs any config change), blast radius (one machine vs fleet), reversibility (was recovery possible without user intervention), detection source (user-reported vs gate-caught vs silent), and the relationship to the trust-ladder incident classes in AGENTS.md (Class A-D are about agent behavior; this definition is about system failures — the two vocabularies must not collide). Deliverable: a definition recorded in the governance docs with examples drawn from real incidents (the 2026-10-29 mise/gateway chain, the fabric auto-bump, the backlog draft-3 failures), and the decision-1 capture rule updated to reference it. Done when: the definition distinguishes captured incidents from ordinary bugs and hotfixes with concrete examples, and a reader can classify a new failure without asking.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A definition exists in the governance docs with concrete examples from real incidents
- [ ] #2 The definition distinguishes captured incidents from ordinary bugs and hotfixes
- [ ] #3 The definition does not collide with the trust-ladder Class A-D vocabulary (system failures vs agent behavior)
- [ ] #4 decision-1 references the definition once it exists
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
