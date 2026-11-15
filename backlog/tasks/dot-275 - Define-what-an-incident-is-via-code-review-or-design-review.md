---
id: DOT-275
title: Define what an incident is via code review or design review
status: To Do
created_date: 2026-10-29 23:38
references:
- backlog/decisions/decision-3 - VM-verify-config-and-symlink-deployments-before-apply-merge-and-PR-gates.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per decision-3 amendment (2026-10-29): before incidents can be captured mechanically as backlog post-mortems, the repo needs an agreed definition of what counts as one. The author requires a code review or design review session to define the boundary. Candidate axes to settle: severity threshold (destabilized user-level usage vs any config change), blast radius (one machine vs fleet), reversibility (was recovery possible without user intervention), detection source (user-reported vs gate-caught vs silent), and the relationship to the trust-ladder incident classes in AGENTS.md (Class A-D are about agent behavior; this definition is about system failures — the two vocabularies must not collide). Deliverable: a definition recorded in the governance docs with examples drawn from real incidents (the 2026-10-29 mise/gateway chain, the fabric auto-bump, the backlog draft-3 failures), and the decision-3 capture rule updated to reference it. Done when: the definition distinguishes captured incidents from ordinary bugs and hotfixes with concrete examples, and a reader can classify a new failure without asking.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A definition exists in the governance docs with concrete examples from real incidents
- [ ] #2 The definition distinguishes captured incidents from ordinary bugs and hotfixes
- [ ] #3 The definition does not collide with the trust-ladder Class A-D vocabulary (system failures vs agent behavior)
- [ ] #4 decision-3 references the definition once it exists
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

**The deliverable is a decision procedure, not prose (2026-11-14).** The
author's aim for this flow is that agents and sessions can call it, and
eventually that it refactors into a shareable skill (DOT-358). A definition
written as governance prose for a human reader is not callable: two agents
classifying the same failure can read it and disagree. So the output this task
owes is an ordered set of questions with worked examples, such that the same
failure reaches the same verdict regardless of who runs it. The four acceptance
criteria above are unchanged by this — severity threshold, blast radius, the
bug/hotfix boundary and the Class A-D collision are still the axes to settle,
and the examples named in the description are still the material. Only the
output format changes.

This task gates the capture half of the flow. DOT-357 owns retirement and does
not depend on this definition; DOT-358 (the skill) depends on both and reads
this task's status as its own prerequisite check — `To Do` means the skill
stops and says why rather than guessing a classification.

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
