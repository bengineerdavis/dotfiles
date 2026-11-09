---
id: DOT-317
title: changelog collector never deletes fragments — mv-then-git-rm ordering is dead
  code
status: To Do
created_date: 2026-11-09 00:07
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`.github/workflows/changelog.yml` collects a PR's changelog fragments into
CHANGELOG.md but never deletes the source fragments. Every collect commit
changes only CHANGELOG.md; the `changelog.d/*.md` files accumulate as orphans.

Root cause is an ordering bug in the "Collect only this PR's fragments" step:
the script first `mv -- "$fragment" "$work/fragments/"` (moving the fragment
out of the repo into a scratch dir), then later loops over the *original*
`fragments-to-collect` list and runs `git rm` only when `[[ -f "$fragment" ]]`
— but the file is already gone, so `git rm` never fires and the deletion is
never committed. The second loop is dead code.

Measured 2026-11-08: collect PR #145 (`b8c3382`) and collect PR #147
(`b8bd406`) both wrote CHANGELOG entries but left their source fragments
tracked on main. Same for PR #135 (`32913ff`): the `lore_help_trap` fragment
content is under PR #135 in CHANGELOG but the file still lingers. Orphans were
manually `git rm`'d for #145/#147 in f2d02d1; the #135 fragments are another
PR's and are not swept here.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- The collector deletes each fragment it collects from `changelog.d/`, in the
  same commit that adds the CHANGELOG entry.
- Fix direction: `git rm` the fragments BEFORE `mv` (or `git rm` from the
  scratch dir's corresponding repo path), so the deletion lands. A test feeds
  a synthetic PR with one fragment and asserts both changelog entry and
  fragment removal.
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
