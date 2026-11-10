---
id: DOT-341
title: Make dotagents client wiring tolerate an absent CLI, and fail loudly on real
  errors
status: To Do
created_date: 2026-11-10 06:04
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

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
