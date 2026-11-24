### Fixed

- **The suite-baseline gate no longer passes a run that executed nothing.**
  pytest exits 5 on an empty selection with `no tests ran`, which IS a summary
  line, so the summary-presence check accepted it. A run that proves nothing is
  now an error, as is a summary claiming failures the log never lists.

- **Node IDs containing spaces are parsed whole.** The parser captured `\S+`, so
  a parametrize id stopped at its first space and the baseline was hand-edited to
  the truncated form. A different test whose id shared that prefix would have
  truncated to the same entry and passed unseen. The two `tests/docs` entries now
  carry their full ids.

### Changed

- `AGENTS.md` § Known failures now separates trunk red from three classes that
  fail only on a developer machine — a stale deployed `~/bin/pii-redactor`, zsh
  living off the harness's pinned `PATH`, and a cached npx dotagents. Adding
  those to the baseline would blind the gate wherever the cause is fixed.
