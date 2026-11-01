---
id: DOT-279
title: Offer source-level batch approval for undeclared skill findings
status: To Do
created_date: 2026-10-30 06:36
labels:
- skill-trust
- ux
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Author request 2026-10-29: resolving an entire repository/source should not require answering one prompt per skill. Code inspection confirms declared skills already offer approve source; undeclared findings carry source=None and only offer vendor/deny/leave, even when an inventory or manager could establish a common origin (as with a roborev-generated family). Extend the public resolve workflow to group eligible undeclared findings by a verified source and offer one explicit source approval with one required why. Do not infer a source merely from a skill name. Explicit per-skill deny/exclude decisions must still win; foreign buckets and hidden directories stay outside this convenience action. Persist each decision as it is made and re-judge afterward. DOT-1 remains the separate recorded-denial revisit workflow.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Two or more eligible findings with the same verified source can be approved in one prompt with one why, not one prompt per skill
- [ ] #2 Source approval applies only to findings whose source the manager/inventory establishes; undeclared source=None findings retain the existing safe choices
- [ ] #3 Explicit deny/exclude rules, foreign buckets, and hidden directories are not silently approved by the batch action
- [ ] #4 Tests exercise both approval and refusal and fail against the old one-prompt-per-skill behavior with mutation evidence
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
