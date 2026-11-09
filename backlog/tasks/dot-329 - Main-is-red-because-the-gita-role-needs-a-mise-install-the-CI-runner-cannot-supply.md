---
id: DOT-329
title: Main is red because the gita role needs a `mise install` the CI runner cannot supply
status: To Do
created_date: 2026-11-08 18:05
labels:
- bug
- testing
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**`main` is red as of 2026-11-09.** PR #152 (`agent/gita-registration`) merged
and six `tests/gita` cases have failed in CI ever since. Every open PR now
inherits those failures and reads as broken.

Measured on run 42567895567 (main, `6b9f266`) and identically on PR #148's
run 42568777363 — same six node IDs:

```
tests/gita/test_work_registration.py::test_check_mode_writes_no_registration_state
tests/gita/test_work_registration.py::test_missing_work_root_skips_reconciliation_without_failing
tests/gita/test_work_registration.py::test_registration_includes_local_only_repos_and_preserves_ghosts[GITA_PROJECT_HOME]
tests/gita/test_work_registration.py::test_registration_includes_local_only_repos_and_preserves_ghosts[None]
tests/gita/test_work_registration.py::test_registration_includes_local_only_repos_and_preserves_ghosts[XDG_CONFIG_HOME]
tests/gita/test_work_registration.py::test_teardown_removes_work_group_before_fake_mise_unuse
```

**The failure, verbatim:**

```
assert proc.returncode == 0, proc.stdout + proc.stderr
E  assert 2 == 0
tests/gita/test_work_registration.py:140
```

with the ansible play reporting:

```
fatal: [localhost]: FAILED! =>
    changed: false
    msg: 'gita not found on PATH after the mise entry ran.
          Fix: run `mise install`, then re-run this topic.'
```

**Root cause class.** The role claims a `pipx:gita` entry through `mise`, then
asserts the binary is on PATH. On a developer machine the entry is already
installed, so `mise install` has run at some point and the check passes. On a
fresh CI runner the entry is declared but never materialised, so the assert
fires. The role is behaving correctly — a declared entry with no binary should
fail loudly — so **the test is the thing standing on a provisioned machine**,
not the role.

That is the same shape as the CI suite portability work in PR #126/#132: tests
that reach for a provisioned machine where the subject allows them to be
hermetic.

**Why it is not simply a baseline addition.** Adding six node IDs to
`EXPECTED_FAILURES` would make the gate green on a condition that every PR
hits, which is what the baseline rule is meant to prevent — the rule says fix
it or record it deliberately, and six CI-only failures in a suite that landed
yesterday look like a portability bug rather than accepted debt.

**Note on the stale baseline.** The same CI runs print:

```
note: 12 baseline entr(ies) did not fail.
```

Those are the `tests/clipped` and `tests/restart_stale` entries, which now pass
post-DOT-73. They are a note rather than a failure (`check_suite_baseline.py:107`),
so they do not block — but the table and `AGENTS.md` § Known failures both
still list them. That refresh is **DOT-314's**, not this task's; do not fold it
in.

**Local reproduction is not available.** `tests/gita` does not exist on
branches cut before PR #152, so a session on an older branch cannot reproduce
this without rebasing onto current main first.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The failing cause is confirmed on a machine that can reproduce it — the `mise` entry state and the missing binary shown — rather than inferred from the CI message alone
- [ ] #2 `tests/gita` runs green on a fresh checkout that has never run the gita topic, or the test states in its own docstring what it needs provisioned and why a fake cannot stand in
- [ ] #3 The fix distinguishes "the role is right to fail" from "the test needs a provisioned machine": if the assert is correct, the test supplies the precondition; if the precondition cannot be faked, the role's contract is what changes, and the reasoning is recorded either way
- [ ] #4 Each new guard is proven by a mutation that fails the right test, recorded as `Mutation:` and `Failing-test:` trailers
- [ ] #5 CI on `main` is green again, verified by a run linked on the task
- [ ] #6 `EXPECTED_FAILURES` is **not** extended with these six node IDs unless the task records why they are accepted debt rather than a portability bug
- [ ] #7 The stale `clipped`/`restart_stale` baseline entries are left to DOT-314, and the task says so rather than quietly changing them
<!-- AC:END -->

## Implementation Notes
<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Start by rebasing onto current `main` — the suite does not exist on older
branches.

The existing suite already has a `fake_mise` concept and an autouse sandbox
fixture that redirects `HOME`, `XDG_CONFIG_HOME`, and `XDG_DATA_HOME` into
`tmp_path`; check those before inventing a new seam. `AGENTS.md` records that
the `$HOME` sandbox is the enforcement vehicle for the no-real-`$HOME` rule, so
a fix that writes outside it is the wrong shape.

`tests/gita/test_work_registration.py:140` is the assert (`proc.returncode ==
0`); the message that matters is emitted by the role, not by the test, so read
the task that raises it to see which PATH lookup is satisfied on a developer
machine.

Related: PR #152 (introduced the suite); DOT-73 (Done — the two suites the
baseline still lists); DOT-314 (baseline refresh, owned elsewhere); PR #126 and
PR #132 (the CI portability work this repeats the shape of); DOT-324 (a
different, machine-specific reason a local run is not green).
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `main`'s CI is green, and a fresh checkout can run `tests/gita` without anyone having run the gita topic first
<!-- DOD:END -->
