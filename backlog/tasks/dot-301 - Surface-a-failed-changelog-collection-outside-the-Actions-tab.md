---
id: DOT-301
title: Surface a failed changelog collection outside the Actions tab
status: To Do
created_date: 2026-11-07 18:44
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make a failed changelog collection visible without opening the Actions tab.

Raised in PR #136's "deliberately left out" list: "No alerting. A red
collection run is still only visible in the Actions tab. Out of scope here."

The failure mode is not hypothetical, and its cost was measured. PR #106 merged
2026-10-30; its collector built the commit correctly and lost the push seven
seconds later to PR #107. The run went red. **Nobody saw it for a week.** The
LoreAI rootless-Lima work sat in the repo with no `CHANGELOG.md` entry until a
session noticed by hand and PR #133 recovered it.

The workflow now retries a rejected push up to three times, which closes the
race that caused #106. It does not close the notification gap: when the retry
gives up it prints `::error::...` into a log nobody is watching. A collection
that exhausts its retries, or fails for a new reason, is still silent.

The bound worth keeping in view: this is one workflow on a single-author repo.
The answer should cost near nothing. A GitHub issue opened by the workflow, or
a line in the job summary, is proportionate; a paging integration is not.

Note what makes this tractable: the collector already knows the exact failure
it is reporting — the error message names the PR whose fragment is still
uncollected, and `workflow_dispatch` (added in #136) is the recovery path. So
the notification can carry the fix, not just the alarm.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A collection that fails after its retries produce a durable, discoverable signal that is not a log line — an issue, or a job summary that persists
- [ ] #2 The signal names the PR, the fragment still on `main`, and the `workflow_dispatch` re-run that fixes it
- [ ] #3 A successful collection produces no signal — the notification must not become noise that gets ignored
- [ ] #4 The mechanism adds no new dependency and no new secret to the repository
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A deliberately failed collection leaves a signal a reader finds without opening the workflow log
<!-- DOD:END -->