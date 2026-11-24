### Fixed

- **The suite-baseline gate reads JUnit XML instead of the pytest log.** The log
  has no reliable delimiter between a node ID and its explanation and no
  unambiguous summary line, so a text-parsing gate was wrong in four ways: a
  parametrize id containing ` - ` was truncated to a baseline entry, `1 failed,
  10 passed, 1 error` hid the error, a test failing in its body and erroring in
  teardown was rejected as a complete log, and captured output resembling
  `=== 999 failed` claimed 999 outcomes. A run that executed no tests is also an
  error now, where `no tests ran` used to read as a pass.

- `junit_family=xunit1` is pinned in the workflow. It is the family that emits a
  `file` attribute; without it the node ID would have to be inferred from a
  dotted classname, which breaks on a test file with a dot in its name. The gate
  refuses a report it cannot identify rather than guessing.

### Changed

- `AGENTS.md` § Known failures separates trunk red from failures that are local
  to a developer machine — zsh off the harness's pinned `PATH`, and a cached npx
  dotagents whose antigravity target relocates skills to `~/.gemini/config`
  (DOT-401). Adding those to the baseline would blind the gate.
