# pytest result-reporting: what to use for the baseline gate

Researched 2026-11-24, after roborev job 853 found four defects in a
text-parsing gate. Requirement, sources, ranking, decision, rejections.

## Requirement (one sentence)

Compare a pytest run's failures against an exact known-failure allowlist and fail
the gate when the run did not complete or an unexpected failure appears —
**mechanically, without depending on pytest's human-readable summary text**.

**Disqualifying capability:** cannot give exact node IDs (spaces, brackets, ` - `),
or cannot distinguish "ran and passed" from "did not run".

A candidate that fails either disqualifier is out, regardless of adoption.

## Sources consulted (three kinds)

1. **Established tool — pytest's own CLI.** `pytest --help` (9.1.1) confirms
   `--junitxml/--junit-xml`, plus `junit_family`, `junit_logging`,
   `junit_log_passing_tests`, `junit_duration_report`, `junit_suite_name`.
   `--report-log` is **absent** — it belongs to the third-party pytest-report-log
   plugin, not core.
2. **Standard — JUnit XML.** The de-facto CI test-report format across languages;
   `<testsuites>/<testsuite>/<testcase>` with `tests`, `failures`, `errors`,
   `skipped` attributes and `<failure>`/`<error>`/`<skipped>` children.
   Jenkins, GitLab, Azure DevOps, CircleCI parse it natively; GitHub Actions does
   not, and hands it to an action or a script.
3. **Practitioner reports.** Multiple CI write-ups make the same point — "your CI
   tool should understand your test results, not just display your logs" — and
   list the standard caveats: pin `junit_family=xunit2`, keep
   `junit_log_passing_tests` off (huge files), avoid ids derived from `repr()` of
   objects with addresses (unstable between runs).

## Verified against the artifact (not recall)

Every disqualifier was tested against real pytest 9.1.1 output:

| Behaviour | Text log | `--junitxml` |
|---|---|---|
| Param id containing ` - ` | `FAILED …test_rule[a - b]` — ambiguous split | `name="test_rule[a - b]"` exact |
| Param id with spaces/brackets | truncated by `\S+` | preserved verbatim |
| `1 failed, 10 passed, 1 error` | `error` after `passed` missed | `errors="1"` attribute |
| Fail in call + error in teardown | 2 lines, 1 ID — set collapses them | **two `<testcase>`**, same name |
| Captured output resembling a summary | `=== 999 failed` wins if taken first | no summary text exists |
| Empty selection | `no tests ran` looks like a summary | `tests="0"` |
| Exact file path | printed in the id | `file=` attribute under `junit_family=xunit1` |

The `file` attribute is the reason to use **xunit1**, not xunit2: under xunit1
pytest emits `file`, `line`, `classname`, `name`, so the node ID is assembled from
`file` + `::` + `name` rather than inferred by turning dots back into slashes.
That inference would work today (no dotted filenames exist in `tests/` or
`tools/`), but it is a guess that a future `test_v1.2.py` would silently break.

## Ranking, leading with the disqualifying capability

1. **`--junitxml` with `junit_family=xunit1`** — passes every disqualifier.
   Built in, no dependency, exact IDs, real counts, distinguishes empty from
   passing. **Selected.**
2. **`--report-log` (JSON lines)** — would also pass, and is pleasant to parse.
   Disqualified: **not in core**, needs the pytest-report-log plugin, adding a
   dependency to CI for no capability JUnit lacks.
3. **Harden the text parser** (bracket-aware ID extraction, parse summary
   components independently, take the last summary line, count per-kind) —
   disqualified: all four findings are symptoms of one root cause, and this fixes
   each symptom while keeping the cause. It also cannot distinguish an
   explanation containing ` - ` from an ID boundary in principle.
4. **Exit codes only** — disqualified: no node IDs, so it cannot implement an
   allowlist at all.
5. **Third-party reporter action** (`dorny/test-reporter`, `EnricoMi/publish-unit-test-result-action`)
   — disqualified for *this* purpose: they publish results into the UI, which is
   a different requirement. The gate needs to make a decision and exit nonzero.

## Decision

Parse `--junitxml` output written by the test step, with `junit_family=xunit1`.
The gate becomes structural: assert a report file exists, read counts from the
`testsuite` element, build node IDs from `file` + `name`, and compare the failure
set to `EXPECTED_FAILURES`. Delete the text parsers entirely rather than leaving
them as a fallback — a fallback that still has the ambiguity is how the old
behaviour comes back.

**Incumbent as baseline to beat:** the text parser was already in place and
"already installed" is not evidence of fit; it failed the disqualifier outright.

## Rejected options, with reasons

- **`--report-log`**: correct but not core → a dependency for no unique capability.
- **Hardened text parsing**: fixes symptoms, keeps the ambiguous format.
- **Exit-code-only gating**: cannot express an allowlist.
- **Reporter actions**: publishing, not gating.
- **`junit_family=xunit2`**: no `file` attribute, forcing path inference from
  `classname` dots. Rejected as a guess, though it is what most parsers prefer —
  this parser is ours, so it can take xunit1.

## Note on CI shape

GitHub Actions has no native JUnit display; that is fine here because the gate
parses the file itself. The existing log upload stays, so a red job still ships
its output for a human to read.
