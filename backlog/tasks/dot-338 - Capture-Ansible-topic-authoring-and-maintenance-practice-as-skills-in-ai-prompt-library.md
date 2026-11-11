---
id: DOT-338
title: Capture Ansible topic-authoring and maintenance practice as skills in ai-prompt-library
status: To Do
created_date: 2026-11-10 04:55
labels:
- ansible
- tooling
- agents
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The repo settles how a topic is written across `docs/TOPIC-RECIPES.md`, `docs/TOPICS.md`, `AGENTS.md` and `spec.md`, but an agent writing a topic re-derives those rules or misses them. A skill is the form an agent loads at the moment it writes one. Two bodies of practice are missing: how to author a topic, and how to keep one healthy as ansible-core and its collections move.

Ship:

- A skill in `ai-prompt-library` covering authoring: the module-vs-shell ladder and support grade, the bare-top-level-fact prohibition, check-mode honesty, the tag producer-superset rule, the teardown counterpart, and the service stable-path rule.
- A skill in `ai-prompt-library` covering maintenance: an ansible-core pin bump triggers a deprecation triage pass, collection drift, scoped ansible-lint, and the upstream-reference check.
- Both declared for this repo through the dotagents source catalogue, when the wildcard source entry does not already cover them.

Constraints:

- Authoring happens in `ai-prompt-library` per the `AGENTS.md` ladder (skills are AI work). This repo files the routing record only; precedent DOT-219.
- Working in the foreign repo needs the maintainer acknowledgement AGENTS.md § Cross-repo changes requires before anything is staged there.
- `docs/` stays the source of truth for repo-specific rules. A skill points at them instead of restating them, because two normative statements of one rule drift apart.
- One skill versus several is a decomposition decision inside this task: split when a reviewer could accept one part and reject another.
- DOT-62 owns the upstream-reference cadence. The maintenance skill cites it rather than duplicating it.

Drafted 2026-11-09 after an `ansible_env` deprecation warning reached a production run; the gap that produced it is DOT-339 (migration) and DOT-340 (gate).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Two skills exist in ai-prompt-library, one covering topic authoring and one covering topic maintenance, each with a description that says when to load it.
- [ ] #2 The authoring skill states the module-vs-shell ladder and support grade, the bare-fact prohibition, check-mode honesty, the tag producer-superset rule, the teardown counterpart and the service stable-path rule, each pointing at the docs file that carries the binding rule.
- [ ] #3 The maintenance skill states what an ansible-core pin bump obliges (a deprecation triage pass), plus collection drift, scoped ansible-lint and the upstream-reference check, and cites DOT-62 instead of restating the cadence.
- [ ] #4 The dotagents source catalogue records whether the wildcard ai-prompt-library entry covers both skills, and a declaration is added only if it does not.
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
