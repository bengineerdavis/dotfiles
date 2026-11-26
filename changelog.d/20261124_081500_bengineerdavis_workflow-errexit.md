### Fixed

- **The test step no longer dies before recording pytest's status.** GitHub runs
  each `run:` block under `bash -e` with pipefail, and pytest exits 1 on the
  normal path where only known failures occur. With errexit on, the pipeline
  aborted at `tee` and neither the status file nor the comparison step ever ran,
  so the job went red for a reason nobody could read. The step now disables
  errexit around the pipeline, captures `PIPESTATUS[0]` immediately, and
  restores it.

- The gate's exit-status argument is **required**. A default read as "probably
  fine", which let a hand-run gate approve an interrupted run whose remaining
  tests never executed.

### Changed

- `AGENTS.md` describes what the gate actually consumes — JUnit XML plus the
  recorded exit status — and lists each refusal with its reason, replacing the
  obsolete description of log parsing and the missing-summary check.
