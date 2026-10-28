---
id: DOT-260
title: 'DRAFT: Evaluate full antsibull-changelog adoption for Ansible topics'
status: To Do
created_date: 2026-10-28 17:48
labels:
- ansible
- docs
- design
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The maintainer wants to keep antsibull-changelog conventions because topics are Ansible roles, but full adoption is not a current priority. Today the loreai topic has a hand-written CHANGELOG.md that uses antsibull-style section names such as minor_changes, release_summary, and known_issues; it is not a generated antsibull changelog. A previous edit removed only a duplicated explanation, leaving the header and sections intact. Research full adoption across Ansible topics: changelog fragments, changelogs/changelog.yaml, antsibull-changelog release, versioning/release workflow, and how per-topic changelogs survive being lifted into another repository. Compare with the existing dated Markdown convention and scriv workflow; do not introduce two competing release processes. Preserve the current format until the design is approved. Consider how the topic-template extraction (DOT-210) should represent the chosen approach.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document the current hand-written Markdown versus full antsibull-changelog behavior and the migration tradeoffs.
- [ ] #2 Recommend whether and when to adopt full antsibull releases across Ansible topics, including generated-file ownership and release/versioning policy.
- [ ] #3 If adopted, update the topic-template design so new topics receive the chosen changelog mechanism without a model.
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
