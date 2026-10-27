---
id: DOT-78
title: Give every topic a TDD-style test suite, and make editing a topic require its
  tests
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Give every topic a TDD-style test suite, and make editing a topic require
  its tests.** `tests/topics/` holds exactly one file — `test_zsh_layout.py`,
  about zsh fragment placement — against the 27 topics under `dotfiles/apps/`,
  so nothing tests what a topic's lifecycle actually does: that every state
  install creates has a teardown in remove (the CRUD invariant `docs/TOPICS.md`
  asserts but nothing checks), that `topic_os` and `topic_requires` match what
  the tasks really use, that `--tags upgrade` touches what it claims and no
  more. Nothing links a topic edit to tests either — the `bats` pre-commit hook
  matches `^(bin|scripts)/` shell scripts only, so changing a topic's YAML runs
  nothing and prompts nothing. **A topic's tests live with the topic** —
  `dotfiles/apps/<topic>/tests/`, not a central `tests/topics/` — so a topic
  stays portable: copy or extract the directory and its tests come with it,
  which is also what makes the `ai-strategy` bundle and the Refactor B
  extraction below movable rather than a re-write. Three things that costs, all
  of which the implementation has to answer: `pytest.ini` sets
  `testpaths = tests tools`, so topic-local suites are not collected today and a
  bare `pytest` would silently pass while testing none of them; `.chezmoiignore`
  ignores a bare `tests/`, so confirm whether that already excludes topic-local
  test dirs from the deployed tree and decide whether it should, since
  portability argues for shipping them so a provisioned machine can verify
  itself; and `dotfiles/template_dir/` has no `tests/`, so the scaffold must
  grow one or topic 28 starts untested by default. Tests first on the next topic
  changed, per the pytest doctrine in `AGENTS.md` and `docs/PYTHON.md`, then
  backfill rather than pausing to write 27 suites up front. **herdr is the
  proven instance** (2026-09-19): full test-first via the author-swarm +
  judge loop, 116 tests in central `tests/herdr/` — the destination stays
  topic-local suites over a shared harness, and the enforcement gate (a
  topic edit forces its tests) is the unlanded half. Done when a
  per-topic suite lives beside its topic over a shared harness (so topic 28
  inherits it instead of re-inventing it), collection reaches those suites, a
  staged change under `dotfiles/apps/<topic>/` runs that topic's tests and fails
  the commit when they are red or absent, and the tap-trust fix in `e60982c`
  has the regression test it went in without — trust-before-tap ordering, and a
  teardown that clears both the tap and the formula trust entry.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
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
