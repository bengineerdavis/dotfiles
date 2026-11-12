---
id: DOT-354
title: 'CI is red on main: 14 failures outside the known-failure baseline'
status: To Do
created_date: 2026-11-12 22:07
labels:
- ci
- tests
updated_date: 2026-11-12 22:08
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Why: `main` already fails the CI baseline gate, so a green run
stopped distinguishing a good change from a broken one. The gate treats any
outcome outside `EXPECTED_FAILURES` as an error, so every branch inherits the
red.

Measured 2026-11-12 on this machine, at base commit `e2f9f429` and again on
`pii-redactor-streaming`: identical 14 failures. Not caused by the
pii-redactor move.

Two distinct groups, and they are not equally interesting:

- `tests/topics/test_opencode_config_layers.py` — 12 failures. Rendering and
  layering assertions for the opencode config (permissions arrays, deep-agent
  rendering on both OS legs, shell catch-all ordering). Likely a rendering or
  fixture drift, not a config regression; unconfirmed.
- `tests/docs/test_lore_md_rules_survive.py` — 2 failures. These assert that
  specific rule anchors survive Lore's re-distillation, and the anchors are
  absent from `.lore.md` **as committed on main**. That is the real signal:
  the test exists because re-distillation once deleted a rule, and it is now
  reporting exactly that. The test's own message says to treat `.lore.md` as
  captures-only and report upstream rather than hand-edit the rule back.

Ship: every one of the 14 is either fixed or, where the behavior is genuinely
expected, added to `scripts/check_suite_baseline.py` EXPECTED_FAILURES *and*
AGENTS.md § Known failures in the same commit. The lore pair must not be
baselined without a decision on whether the rule loss is real.

Constraints:
- Do not baseline a failure that has not been diagnosed. A baseline entry is a
  claim that the failure is expected, and 12 undiagnosed render failures is not
  that claim.
- The lore anchors are content loss in a file Lore manages; the fix may belong
  upstream (DOT-305 / DOT-298 pattern) rather than in this repo.
- Verify at the base commit before blaming a branch: `git worktree add
  .worktrees/base-check <base-sha>`, run the same tests, remove it.

Open questions:
- Are the 12 opencode failures environmental (this machine) or real on a runner?
  CI runs ubuntu-latest; the render tests name both darwin and linux legs.
- Was the `.lore.md` rule loss a deliberate re-distillation decision or a
  regression? `git log -p -- .lore.md` around commit 107b34d5 should say.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The 12 `tests/topics/test_opencode_config_layers.py` failures are diagnosed, not baselined: each is either fixed or has a stated reason it is expected.
- [ ] #2 The 2 `tests/docs/test_lore_md_rules_survive.py` failures are resolved by a decision on the rule loss — restored, re-anchored with the test updated, or recorded as upstream breakage — not by deleting the assertion.
- [ ] #3 `scripts/check_suite_baseline.py` EXPECTED_FAILURES and AGENTS.md § Known failures agree, changed in the same commit.
- [ ] #4 `uv run --frozen python scripts/check_suite_baseline.py <log>` exits 0 on a clean run from `main`.
- [ ] #5 Any failure kept in the baseline names the reason it is expected, so a reader can tell a known failure from a forgotten one.
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
