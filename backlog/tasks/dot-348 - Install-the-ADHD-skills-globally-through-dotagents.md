---
id: DOT-348
title: Install the ADHD skills globally through dotagents
status: To Do
created_date: 2026-11-10 20:55
assignee:
- opencode-dotagents-adhd
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Neither requested skill is installed or declared, although dotagents 3.4.0 is the machine's global skill manager. The author approved installing both upstream sources directly and recording verified integration corrections with the topic.

Ship:

- Add UditAkhourii/adhd and ayghri/i-have-adhd to dotagents_sources with reviewable trust and licence evidence.
- Record verified plugin discovery, OpenCode projection, and native-adapter limits in the dotagents topic docs, including correction of the stale opencode-only claim.
- Extend docs/TOPICS.md so verified topic-specific corrections and current upstream references stay with each topic for future maintainers and topic skills.

Constraints:

- Do not fork either upstream project for the core skill install.
- Do not install i-have-adhd's OpenCode command, plugin hook, or always-on flag in this task; those belong to the queued follow-up.
- Deployed-tree changes require a branch, PR, and human review. Do not run chezmoi apply or mutate the live agent configuration.
- Leave other sessions' queue and worktree changes untouched.

Decision record: Approved by the author 2026-11-10: upstream dotagents sources now; native OpenCode adapter and upstream documentation work queued separately.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Both approved upstream sources are declared in dotagents_sources with verified licence and trust rationale.
- [ ] #2 The dotagents topic docs distinguish verified behavior from untested projections and no longer claim plugin sources are opencode-only.
- [ ] #3 docs/TOPICS.md requires topic-specific corrections and authoritative references to live with the topic.
- [ ] #4 New or changed tests have been seen to fail against the unfixed tree, with Mutation and Failing-test trailers on the implementation commit.
- [ ] #5 Focused tests, documentation integrity checks, and skillet validation pass on the implementation branch.
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
