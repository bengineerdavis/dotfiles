---
id: DOT-341
title: Make dotagents client wiring tolerate an absent CLI, and fail loudly on real
  errors
status: To Do
created_date: 2026-11-10 06:04
orchestration:
  status_key: inprogress
  lease_owner: dotagents-optional-clients
  lease_expires_at: '2026-11-10T07:04:22.697723Z'
  version: 1
updated_date: 2026-11-10 06:16
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
apps/dotagents wires the dotagents-local plugin marketplace into each agent CLI, but assumes every CLI is installed. On the Debian box `claude` is absent (apps/claude-code is deliberately `topic_os: [Darwin]`; Debian support is DOT-141), so `claude plugin marketplace add` fails with rc 127 and the run aborts. The failure message then reports "nothing on stderr", because Ansible puts command-not-found in `msg` while the fail task maps only `stderr` — the one detail naming the cause is dropped.

Ship:

- install.yaml probes each optional client CLI (`claude`, `codex`) on the extend PATH and skips wiring for a client that is absent, reporting which clients were skipped and why.
- The fail tasks report `stderr`, then `stdout`, then `msg`, so a missing binary names itself instead of printing "nothing on stderr".
- A per-client opt-out (default on) so a machine can decline wiring for an installed client deliberately, rather than by absent binary.

Constraints:

- Owned by apps/dotagents; no per-agent topic is created. Absence of a client is a supported state, not an error: the topic still installs the skill set.
- A present client that fails for a real reason still fails the run — the gate must be proven to relent as well as to decline.
- Wires to `claude plugin` only when the binary exists; do not template ~/.claude/settings.json (machine-local).
- Unblocked by evidence: `claude plugin marketplace add` writes a user settings file and needs no auth (code.claude.com/docs/en/plugins/cli-reference, read 2026-11-09), so auth is not a precondition and no credential probe is needed.

Decision 2026-11-09: absence is gated on the binary, not on OAuth or API credentials — plugin registration is a local settings write, so no token is read and no headless auth attempt is made.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A machine without claude or codex completes apps/dotagents install with the skill set in place and a report naming the skipped clients
- [ ] #2 The fail-message helper renders stderr when present, stdout when stderr is empty, and msg when both are empty (unit-tested against a command-not-found result)
- [ ] #3 A client present but failing for a real reason still fails the run; a mutation removing the failure makes the test fail
- [ ] #4 An installed client with its wiring flag off is reported as declined, not as absent
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Fixed on branch dotagents-optional-clients, PR #172 (2026-11-09). Clients are probed with command -v and classified wired/declined/absent; absence is gated on the BINARY, not credentials — verified from code.claude.com/docs/en/plugins/cli-reference that plugin marketplace add is a local settings write needing no auth. client_said filter reports stderr, then stdout ('Aborted.'), then msg. Measured: --tags dotagents_skills now completes on this Debian box with failed=0, reporting 'claude is absent, codex is wired'. 9 tests; 3 mutations tried and caught. Pre-existing unrelated failure: tests/docs/test_lore_md_rules_survive.py (requires_map anchor missing from .lore.md on main too).
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
event_id: run-732eb5d5bde74ca8b6ef85c660555cb8
type: claim_task
actor: dotagents-optional-clients
timestamp: '2026-11-10T06:04:22.697775Z'
result: succeeded
task_id: DOT-341
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
