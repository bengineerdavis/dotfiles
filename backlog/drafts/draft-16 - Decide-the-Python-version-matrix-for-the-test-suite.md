---
id: draft-16
title: Decide the Python version matrix for the test suite
status: Draft
created_date: 2026-11-05 04:10
labels:
- design
- testing
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design draft only. Do not build from this file; it is the input to a
`/grill-with-docs` session.

The question: should this repo run its test suite against more than one Python,
and if so which, using what tool, and at what cost?

This came out of the 2026-11-04 retro. A repo-wide floor test now scans every
tracked Python file and checks it parses on the oldest interpreter that can run
it (`tests/test_python_floors.py`). That closed the specific bug — `ruff format`
stripping the parentheses off `except (A, B):` into 3.14-only PEP 758 syntax —
but it answers a grammar question, not a runtime one. Nothing here verifies that
the suite itself passes on more than the one interpreter on this machine.

That gap is real but its size is unknown, and that is the point of this draft.

### What is already settled, and not up for re-litigation

- **Runtime policy: latest stable Python.** Author, 2026-11-04: "As a policy, I
  want to use the latest stable version of Python, especially to start moving to
  the threadless python that's stabilizing in 3.15+." A multi-version matrix
  that pins the *development* interpreter backwards would contradict this, so
  any proposal has to say clearly which interpreter is the target and which are
  compatibility checks.
- **Grammar is already covered, cheaply.** `tests/test_python_floors.py` does 147
  files in under a second via `ast.parse(feature_version=...)`, with no extra
  interpreters installed. A matrix would not replace it and should not try.
- **`ruff` is pinned below the runtime floor on purpose.**
  `target-version = "py310"` in `pyproject.toml`, because a formatter has to emit
  code the oldest executor accepts. That is a separate boundary from the test
  matrix and the two must not be conflated.

### What is genuinely open

1. **Is there a second interpreter worth testing at all?** The candidate is not
  an older version but a *variant*: `python3.14t`, the free-threaded build.
  That is where the policy is heading, and 3.14 is the first release where it is
  officially supported rather than experimental. Testing `3.14` against `3.14t`
  is a different proposition from testing `3.10` through `3.14`: same grammar,
  different runtime.
2. **Which interpreters actually execute repo Python, and is that list stable?**
  Three distinct executors exist today, and only one is a project choice:
  `/usr/bin/python3` = 3.10.12 (system, used by Ansible under `become`);
  `python3` on PATH = mise 3.14.8 (used by pre-commit `language: system`);
  the uv-managed environment in `pyproject.toml` = `>=3.14`. Whether the 3.10
  one should remain in the contract is a provisioning question, not a testing
  one, and it may already be answerable by moving the Ansible interpreter.
3. **Does the suite even support a second interpreter?** Unverified. Several
  tests shell out to real binaries and inspect host state; `tests/clipped` and
  `tests/restart_stale` already fail on this host for environmental reasons. A
  matrix over a suite with a known-failing set needs a story for what "passes on
  3.14t" means.
4. **What is the actual cost, measured rather than assumed?** The full suite is
  ~8–11 minutes single-threaded on 32 cores, and the retro already flagged suite
  runtime as the session's dominant cost. A matrix multiplies that. The
  `-n auto --dist worksteal` fast loop exists but is documented as an optional
  footnote, so the real baseline is the slow number.
5. **Does tox fit, or is `uv` already the answer?** tox is the conventional tool
  and what the author asked about. But `uv` already manages interpreters, resolves
  environments, and is the repo's only Python tool. A `uv`-native matrix
  (`uv run --python 3.14t`) may need no new dependency at all, and adding tox
  wants a reason beyond convention. Note `uv run` without `--frozen` re-locks
  `uv.lock` — an established hazard here.

### Constraints worth carrying into the grill

- No CI exists for tests or lint (`.github/workflows/` has only `changelog.yml`),
  so any matrix runs locally or nowhere. A matrix that only runs on one machine
  is a weaker instrument than it appears.
- `uv run --frozen` is mandatory in this repo; a tool that cannot work frozen is
  disqualified.
- Test deps must stay installable under every interpreter in the matrix, or the
  matrix reports install failure rather than code failure.
- Windows is not a target. Debian and macOS are.

### Research to do before the grill

Read, do not guess:

- `uv` docs on managed Python versions and `uv run --python`, to establish
  whether a matrix needs tox at all.
- tox 4 docs on `basepython`, env naming, and `labels`, and tox-uv as the bridge
  if tox is kept.
- The free-threaded build's constraints: which C extensions lack `cp314t` wheels
  yet, and whether this repo's test deps are affected.
- This repo's own evidence: whether any current test is version-sensitive at all,
  versus shelling out to host binaries.

### Explicit non-goals

- Not a rewrite of the floor test.
- Not a change to the runtime policy.
- Not an attempt to make the known-failing suites pass.
- Not a CI pipeline; if the answer implies CI, that is a separate decision with
  its own cost.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Answer, with evidence, whether a second interpreter is worth testing and which one (candidates: 3.14t, the 3.10 system interpreter, none).
- [ ] #2 State which tool runs the matrix and why, comparing `uv` alone against tox/tox-uv, with the rejected option's reason recorded.
- [ ] #3 Give a measured cost per matrix run against the single-interpreter baseline, and say where in the existing tiers it belongs.
- [ ] #4 Define pass criteria for a matrix whose suite has a known-failing environmental set.
- [ ] #5 Say what a matrix would catch that `tests/test_python_floors.py` cannot, or conclude it is not worth building and record why.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Sequencing, per the author (2026-11-04): research and grill with docs first, then
follow the ask-matt flow from there (`/grill-with-docs` → `/to-spec` →
`/to-tickets` → `/implement`). This draft is the input to that grill, not a
design.

A worktree of its own when implementation starts: the working directory is
already carrying a concurrent session's changes, and this work will touch
`pyproject.toml` and the test layout.

Adjacent decisions this depends on, which should not be settled here by
accident:

- The Ansible interpreter question (whether `/usr/bin/python3` stays 3.10) is a
  provisioning decision owned by the apt topic, not by this draft.
- Suite runtime and the known-failing set are draft-9 (tiered fast feedback) and
  DOT-73 territory.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
