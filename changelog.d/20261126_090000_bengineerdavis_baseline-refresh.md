### Changed

- **The known-failure baseline now lists only tests that still fail.** The ten
  `tests/clipped` and two `tests/restart_stale` entries described failures
  DOT-73 fixed; measured 2026-11-26, those suites read **82 passed, 13 skipped**.
  A stale entry is nonfatal, so nothing was broken — but a list that describes
  nothing real cannot be trusted when it matters, and every run printed a
  twelve-line warning telling readers to update it.

  `EXPECTED_FAILURES` and the `AGENTS.md` table moved together, which the drift
  test enforces. Two `tests/docs` entries remain: those are real trunk red from
  the `.lore.md` re-distillation (DOT-305).
