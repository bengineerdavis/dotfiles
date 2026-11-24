---
id: DOT-400
title: Make the dotagents-caller guard find callers it cannot see, and prove it still fails
status: To Do
created_date: 2026-11-19 21:01
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

The guard fixed in PR #187 (commit 237d7be8) now parses task YAML and inspects only command/shell values, so prose that mentions dotagents no longer trips it. That fix closed a false positive. Two questions it left open are recorded here.

Ship:

- Decide whether the guard should also catch a dotagents invocation written as a Jinja expression — `cmd: "{{ some_var }}"` where the variable resolves to a dotagents call. The YAML parse cannot see through that, so such a caller passes the guard while discarding stderr: the original 2026-09-12 bug, restored. Check whether any task in the repo actually does this before treating it as theoretical.
- Add mutation coverage for the guard itself. The current proof lives in a session log and a commit trailer, not in CI: nothing re-runs the two mutations (stderr to stdout, and dropping failed_when) if someone later loosens the matcher again.

Constraints:

- Do not widen the matcher back to a text search to catch the Jinja case; that reintroduces the false positive that turned the gate red for apps/opencode/tasks/install.yaml.
- Keep tests/guards passing, and keep the existing caller mutations failing.

Why this is not part of PR #187: the false positive was a regression that PR introduced and had to fix to merge. These two are hardening, and mixing them into that PR would put two rationales in one change.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 A dotagents caller written through a Jinja variable either fails the guard or is documented as an accepted blind spot with its reason
- [ ] #2 The guard's own mutations run in CI, so loosening the matcher fails a test

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
