---
id: DOT-73
title: Close out the 12 environmental suite failures — the pii half is now diagnosed
status: Done
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-11-07 21:22
orchestration:
  status_key: todo
  version: 4
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
- [ ] #1 The full clipped suite passes hermetically on a machine with real clipboard tools installed
- [ ] #2 clipped copy cannot hang a capturing caller even when the backend forks a lingering child (regression test, mutation-proven)
- [ ] #3 The restart_stale inert tests pass on a systemd host
- [ ] #4 The pii_redactor real-model tests skip with a named reason when the integration model is absent, and still run when present
- [ ] #5 A headless full run reports zero failed with skips named
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Closed via PR #114 (merged 2026-11-05, merge 721a8b3): 10 clipped harness fakes + clipped DEVNULL/temp-file copy fix; restart_stale systemctl --version stub filter; pii_redactor named skip when integration model absent; regression tests mutation-proven. VM-verified 2026-11-07 in lima-mol (Debian 12, real xclip 0.13, headless): clipped suite 42 passed, captured-caller copy completes without hang, failing-backend diagnostic preserved. Full suite 1219 passed / 21 skipped on rebased branch; all roborev reviews closed (248/320/321 findings resolved; 330/331/373 pass). hooks/lychee moved to DOT-281 (landed on main). Lease released on close-out.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->
## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-3c5ce3c3749a4826a5a6292b4443ca48
type: claim_task
actor: opencode-chezmoi-73
timestamp: '2026-11-03T04:14:06.952217Z'
result: succeeded
task_id: DOT-73
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Close out environmental failures: clipped backend-preference + bounded-read fix, systemctl stub filter, pii skip-with-reason
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-122435914512431aa2c3ced414a02783
type: transition_task
actor: opencode-chezmoi-73
timestamp: '2026-11-07T21:22:16.526862Z'
result: succeeded
task_id: DOT-73
from_status: inprogress
to_status: review
```
all roborev reviews closed (248/320/321/330/331/373 resolved or pass); merge quiz passed 3/3; full suite 1219 passed 21 skipped; VM-verified in lima-mol (clipped 42 passed, no hang)
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-6689d12be4794669becdf87da0980438
type: transition_task
actor: opencode-chezmoi-73
timestamp: '2026-11-07T21:22:22.427724Z'
result: succeeded
task_id: DOT-73
from_status: review
to_status: complete
```
PR #114 merged (merge 721a8b3); VM-verified; work closed out
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-4b52e6c65aba4e53a155dcc2710dbed7
type: release_task
actor: opencode-chezmoi-73
timestamp: '2026-11-07T21:22:25.791032Z'
result: succeeded
task_id: DOT-73
from_status: complete
to_status: todo
```
work merged as PR #114; lease was stale since 2026-11-03; released on close-out
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
