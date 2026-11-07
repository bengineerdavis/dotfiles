---
id: DOT-300
title: Add actionlint to CI so workflow edits are checked
status: To Do
created_date: 2026-11-07 18:44
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add `actionlint` to the CI workflow, so a change to `.github/workflows/` is
checked the way every other file in the repo is.

Raised in PR #136's "deliberately left out" list: "No `actionlint`. The
workflow still has no lint step. Worth adding, but it is a separate decision
about what CI runs." That decision is this task.

Why it earns its place, from what the 2026-11-06/07 CI work hit:

- **A fabricated action SHA passed every local check.** `fec0c13` pinned
  `upload-artifact` to a SHA transcribed wrong; it matched the real SHA for 28
  of 40 characters. Nothing caught it until the workflow failed to resolve the
  action at run time. The guard that was later added compares the pin to a
  known value, which covers the pins we know; actionlint is what covers the
  ones we do not.
- **Workflow YAML errors surface as run failures**, not as review findings.
  A shell syntax error inside a `run:` block is a red job on `main` after
  merge, which is the most expensive place to find it.

The repo already trusts a linter for every other language: ruff and Pyrefly for
Python, shellcheck for bash. The workflow files are the one executable artifact
with no static check.

Do not install it into the hook stage: the pre-commit hooks run only where
`prek install` was done, and CI is the layer that has to run everywhere. Wire
it into `.github/workflows/tests.yml` as its own step, reporting through the
same failure surface as the suite.

`actionlint` is not installed on the reference host (`which actionlint` → not
found), so the step needs a pinned acquisition — `mise` entry or a released
binary with a checked SHA — not an assumption that it is on PATH.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `.github/workflows/tests.yml` runs actionlint over `.github/workflows/` on every PR and every push to `main`
- [ ] #2 A deliberately broken workflow (invalid YAML, or an unknown key) fails the job — recorded as a `Mutation:`/`Failing-test:` pair
- [ ] #3 The actionlint version is pinned, and the pin is recorded in `docs/REFERENCES.md` alongside the other standards
- [ ] #4 The new step does not make CI slower than the suite it sits beside by more than a few seconds
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A workflow edit with a real error fails CI before merge
- [ ] #2 `docs/REFERENCES.md` names the actionlint version
<!-- DOD:END -->