---
id: DOT-364
title: Research how agentic projects manage githook installers and concurrent-session
  safety
status: To Do
created_date: 2026-11-15 20:21
priority: high
dependencies:
- DOT-57
labels:
- research
updated_date: 2026-11-15 20:23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
prek's unstaged-change handling is unsafe when sessions share a checkout. It
saves unstaged work to `~/.cache/prek/patches/` and reapplies it after a failed
hook, which twice this session restored an edit a session had deliberately
backed out — a mis-targeted DOT-244 edit after deletion, and another session's
DOT-140 edit after unstaging. prek 0.5.10 exposes no flag to disable it
(`prek run --help`) and never prunes the cache: 635 files, 32 MB, oldest
2026-08-10. DOT-59 evaluated this mechanism in September as a stash-safety
question and correctly cleared it; the multi-session hazard was not in scope.
The installed `setup-pre-commit` skill is Husky and lint-staged for JS
projects, so it does not apply to a Python repo on prek.

Ship:

- Findings on how other agentic projects handle hook runners where several
  agents share one checkout, from primary sources
- A comparison of prek and pre-commit on this specific behaviour, verified
  against each tool rather than recalled, including whether pre-commit's
  stash approach removes this class of error or relocates it
- A recommendation: stay on prek, fall back to pre-commit, or accept the
  behaviour because worktree isolation removes it
- The rejected options recorded with the reason each was disqualified

Constraints:

- Verify behaviour by running each tool, not from docs or memory
- Judge against the requirement — a restore must never resurrect another
  writer's deliberate removal — and rank by that, not by adoption
- Treat prek as the incumbent and the baseline to beat; name what would have
  to be true to justify switching back
- Report if the finding is that DOT-57's worktree isolation makes the question
  moot, rather than recommending a change nobody needs
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Findings cite primary sources on hook-runner behaviour under concurrent sessions
- [ ] #2 prek and pre-commit are compared on restore behaviour, verified by running each
- [ ] #3 A recommendation names one option and what would justify switching
- [ ] #4 Rejected options are recorded with their disqualifying reason
- [ ] #5 The report states whether worktree isolation makes the question moot
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
