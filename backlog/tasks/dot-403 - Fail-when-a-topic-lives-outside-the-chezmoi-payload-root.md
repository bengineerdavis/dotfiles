---
id: DOT-403
title: Fail when a topic lives outside the chezmoi payload root
status: To Do
created_date: 2026-11-25 04:50
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`.chezmoiroot` names `home/` as the chezmoi source state. A topic written
anywhere else still looks complete — `git ls-tree` lists the files, the YAML
parses, and `--syntax-check` passes — but chezmoi never deploys it.

Measured 2026-11-24: a branch cut before the payload moved carried all 13
files of `apps/agentsview` under a top-level `dotfiles/` root that
`.chezmoiroot` does not reach. Committed as-is it would have deployed
nothing while appearing finished. Nothing caught it; the topic was moved by
hand after reading `.chezmoiroot`.

No existing test asserts where a topic directory may live.

Ship a mechanical guard: every `topic.yml` in the repository must sit under
the directory named by `.chezmoiroot`. Fail with the offending path and the
payload root in the message.

Constraints:

- Read the payload root from `.chezmoiroot`; never hardcode `home`.
- A missing `topic.yml` must not silently pass — assert the expected set is
  non-empty, so a broken glob cannot read as success.
- Follow `docs/TESTING.md`: prove the test fails by pointing one topic's
  `topic.yml` outside the root.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A test asserts every `topic.yml` under the repository sits beneath the directory named by `.chezmoiroot`
- [ ] #2 The failure message names the offending path and the resolved payload root
- [ ] #3 The payload root is read from `.chezmoiroot`, never hardcoded
- [ ] #4 The test asserts it found a non-empty set of topics, so a broken glob cannot read as success
- [ ] #5 The test was seen to fail by moving one topic's `topic.yml` outside the root, with the mutation recorded in a `Mutation:` trailer
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
