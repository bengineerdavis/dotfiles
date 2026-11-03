---
id: DOT-73
title: Close out the 12 environmental suite failures — the pii half is now diagnosed
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-11-03 03:18
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Close out the 12 environmental suite failures — the pii half is now
  diagnosed.** The advisor pass found what this queue called undiagnosed:
  the two `tests/pii_redactor` llm failures are model-absence, named by the
  error itself — the conftest (`tests/pii_redactor/conftest.py:29`) requests
  `qwen3.5:4b-mlx-bf16` through the real `llm` CLI and gets
  `Unknown model`; no qwen3.5 model is installed. The snapshot's "runs
  against a mock" claim was wrong for these two tests and is corrected.
  **Machine-stamped:** the absence is the second machine's, 2026-09-14 —
  this Mac HAS the tag (`ollama list`, 2026-09-15), so here the diagnosis
  is unconfirmed until the two tests are re-run.
  Remediation is the author's call: install that model (space
  consideration) or make the conftest skip-with-reason when the integration
  model is absent. The 10 `tests/clipped` failures remain clipboard/TTY —
  each gets an environment skip naming the missing capability or a fix if
  the test is wrong. Run clipped and pii_redactor in SEPARATE pytest
  invocations: one invocation aborts at collection (conftest name
  collision, `from conftest import CLIPBOARD_CONTENT`). Done when a
  headless full run reports zero failed with skips named, and a capable run
  still exercises what was skipped. [me]
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-11-01 diagnosis, this Debian 12 machine: the clipped failures are NOT TTY/clipboard environment gaps — the fake pbcopy/pbpaste harness is sound and xclip works here (DISPLAY=:1, probe rc=0). The real signature: every failing test hangs until subprocess timeout=60 then reports an empty capture. Reproduced minimally outside pytest: fake pbcopy on PATH, `echo hello | ~/bin/clipped copy` returns rc=0 but the capture file never appears; paste works. Suspect the deployed ~/bin/clipped's copy path on this box (backend selection? xclip stealing stdin?) — diagnose from that minimal repro, not from the suite. Also measured: tests/loreai is green here (23 passed 2026-11-01; the parity test passes — its earlier failure was a stale-collection artifact) and tests/restart_stale has 2 real failures: test_the_defaults_leave_the_role_inert and test_a_missing_kind_fails_before_anything_runs both see a [['systemctl','--version']] call the stubs do not filter — Ansible's service_mgr fact-gathering probes systemctl --version through the stub and the tests assert not machine.calls(). That is a harness gap (the ps stub already filters fact-gathering probes; systemctl needs the same treatment), fold it into this task.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->
## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
