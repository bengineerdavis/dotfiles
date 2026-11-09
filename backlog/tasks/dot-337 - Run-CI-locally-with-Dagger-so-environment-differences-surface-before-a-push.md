---
id: DOT-337
title: Run CI locally with Dagger so environment differences surface before a push
status: To Do
created_date: 2026-11-09 16:35
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Local runs and CI disagree in ways that cost a round trip each time, and the
disagreement is always something the local environment supplies that the runner
does not.

Three measured instances, all in one session, all found only after pushing:

- `tests/gita` needs `gita` on PATH. A developer machine has it from
  `mise use -g pipx:gita`; the runner had nothing, so six cases failed on every
  CI run for as long as the suite existed (DOT-329).
- With `gita` installed there, a second failure appeared: the runner exports
  `XDG_CONFIG_HOME`, so a test that meant "no config override" wrote into the
  real path and read from `tmp_path` — green locally, `KeyError` in CI.
- The same shape recurred earlier with `mise` itself, `pyrefly`, and the
  `.molecule` scratch trap: each was a difference between the two environments,
  not a bug in the change under test.

Dagger runs the pipeline in containers locally, so the environment is the one
CI uses rather than the one the laptop happens to have.

Ship:

- An evaluation of Dagger against this repository's CI: what a local run
  would reproduce, what it cannot (macOS-only legs, secrets, the GitHub
  runner image itself), and the cost in time and disk.
- A decision, with the rejected alternatives recorded and their verification
  cited.
- If adopted, a local entry point that runs the same steps the workflow
  defines, kept in step with `.github/workflows/tests.yml` rather than a
  second copy of the same logic.

Constraints:

- Evaluate before building. The alternatives are already installed or nearly
  free — `act`, a `mise run` task wrapping the workflow's commands, or a
  container-based runner — and must be ranked, not skipped, per the
  review-best-practices rule.
- Do not let a local runner become a second source of truth for CI. One
  definition, invoked two ways, or the drift replaces the problem it solves.
- Any secret or network-dependent step stays out of the local path and is
  named as out of scope rather than faked.

Decided with the author 2026-11-09: capture this as a task now so the option is
not lost, after a session spent resolving a CI-only difference by hand.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Dagger is evaluated against this repo's actual CI needs, with the three measured environment-difference cases cited as the evidence the problem is real
- [ ] #2 At least three alternatives are ranked, including `act` and a container-based runner, each with what it does and does not reproduce
- [ ] #3 The macOS-only and secret-dependent parts of CI are named as out of scope for a local run, rather than faked
- [ ] #4 The cost is stated in measured terms — wall-clock time and disk for one local run of the current suite
- [ ] #5 A decision is recorded with the rejected alternatives and the verification behind each claim
- [ ] #6 If adopted, the local entry point invokes the workflow's own definition rather than a second copy of its steps, and the task records how drift is prevented
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
