---
id: DOT-343
title: Fix the backlog daemon bootstrap failing with launchctl rc 5 on macOS
status: To Do
created_date: 2026-11-10 17:36
labels:
- bug
priority: high
orchestration:
  status_key: inprogress
  lease_owner: opencode-dot-343-launchctl-rc5
  lease_expires_at: '2026-11-17T18:18:41.066421Z'
  version: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Darwin bootstrap task in home/dotfiles/apps/backlog/tasks/install.yaml failed on 2026-11-10 with "Bootstrap failed: 5: Input/output error". The plist lints OK and launchd lists the label as enabled, but nothing listens on 127.0.0.1:18765, so the daemon is down.

Ship:

- a reproduction command that goes red on this failure before any fix
- a fix so the bootstrap task converges whether the service is loaded, half torn down, or absent
- a regression test for the task's behaviour

Constraints:

- diagnose before fixing (diagnosing-bugs); the candidate causes are unconfirmed: bootout returning before teardown finishes, `2>/dev/null` hiding a bootout failure, the mise shim in ProgramArguments
- gui-domain launchctl needs no sudo; do not add become
- deployed-tree change: branch, PR, human review
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The reproduction command is recorded in the notes and was seen red before the fix
- [ ] #2 The backlog topic run succeeds twice in a row on macOS and backlog-py daemon status --json exits 0
- [ ] #3 The regression test was seen to fail against the unfixed task (Mutation:/Failing-test: trailers)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
### Reproduction command (AC #1 — seen red before the fix)

```
uv run --frozen pytest tests/topics/test_backlog_daemon_bootstrap.py -q
```

Against the unmodified `install.yaml` this failed 2 of 5 tests with the
reported symptom, from the task's own command run against a throwaway label:

```
E  AssertionError: Bootstrap failed: 5: Input/output error
E    Try re-running the command as root for richer errors.
FAILED tests/topics/test_backlog_daemon_bootstrap.py::test_a_disabled_label_converges
FAILED tests/topics/test_backlog_daemon_bootstrap.py::test_a_disabled_but_loaded_label_converges
2 failed, 3 passed in 17.59s
```

### Confirmed cause (not a guess — measured 2026-11-17)

`launchctl disable` writes a PERSISTENT override into the user's launchd
domain. It survives `bootout` and reboot; only `launchctl enable` clears it.
Bootstrap of a disabled label fails with **rc 5 "Input/output error"** and
leaves the daemon down, and the override is still there afterwards, so every
later run fails the same way.

The task's command was:

```
launchctl bootout ... 2>/dev/null;
launchctl bootstrap ... && launchctl enable ...
```

`enable` sat behind `&&` after a `bootstrap` that cannot succeed while the
label is disabled. So the one command that fixes the state was unreachable
exactly when it was needed — a self-perpetuating failure. The task's own
comment, "bootstrap then enable converge both", was the wrong assumption.

State matrix measured with throwaway labels, same harness, one variable:

| State | Old task | New task |
|---|---|---|
| absent | PASS | PASS |
| loaded + running | PASS | PASS |
| disabled + absent | **FAIL rc=5** | PASS |
| loaded + disabled | **FAIL rc=5** | PASS |

Ruled out by probe, each measured: a missing `StandardOutPath` directory
(bootstrap returns 0 — launchd creates it); a nonexistent program path
(returns 0); `bootout` racing teardown (10/10 clean sequentially, and the fix
keeps a bounded wait anyway — the race is real but not what produced rc 5).

### Why the daemon looked healthy

`backlog-py daemon status --json` exited 0 and port 18765 was open all session
(pid 2564, started 2026-11-16 11:24). The label is currently `enabled` in the
override database, so the failure is not continuous — it appears whenever a
run leaves the label disabled, which is what the 2026-11-10 run did. The
diagnosis therefore rests on the state matrix above, not on the live daemon
being broken right now.

### The fix

Enable unconditionally first (the only step that clears the override and it
must not be gated on a bootstrap that cannot succeed); bootout only a label
`launchctl print` reports (its rc-113/0 exit status is the reliable presence
test — `bootout` of a missing label returns 3); wait for teardown rather than
assuming it is synchronous; then bootstrap and let the existing health check
prove the result.

### Verification

- 5 new tests in `tests/topics/test_backlog_daemon_bootstrap.py` — green in
  1.2s against the fix, 2 red against the unfixed task.
- The test reads the command out of `install.yaml` and renders it against a
  throwaway label, so it cannot drift from the file it protects. The real
  daemon is never touched; every probe label, plist and override was cleaned
  up (verified: no probe labels loaded, no probe plists, real daemon still
  pid 2564).
- YAML parses (10 tasks); the rendered command passes `bash -n`.
- `ruff check` and `ruff format --check` clean.
- `tests/topics` as a whole: 133 passed, 12 failed — all 12 in
  `test_opencode_config_layers.py`, and all 12 reproduce identically on a
  pristine checkout of HEAD, so they are pre-existing and not caused here.

### Not verified

- The full topic run (`executable_run-role.sh backlog`) was **not** executed:
  it installs and would restart the live daemon, which needs the author's
  approval and the apply claim. AC #2 asks for it; it remains open for the
  author to run.

### Branch and PR

- Branch `dot-343-launchctl-rc5`, commits off `c57f945c`:
  - the fix and its five tests
  - this task record
  - branch-state record
  - `4c536b7` the shared `roles/services` role (see below)
- PR opened: **DOT-343 → bengineerdavis/dotfiles PR #181**
  (`dot-343-launchctl-rc5` -> `main`, +1199/-142 across 17 files, mergeable).
  Not merged: the author runs merges, and the merge-readiness quiz comes first.
- `wt switch --create` was used first and **refused correctly** (dirty main in
  the shared checkout, `scripts/sync-task-base.py` fails closed); the worktree
  was then created with `git worktree add .worktrees/dot-343-launchctl-rc5 -b
  dot-343-launchctl-rc5 origin/main`, per docs/WORKTREES.md § Lifecycle.
- All nine AC boxes are still unchecked. #1 and #3 are evidenced above and
  left for the author to tick with the merge, since #2 needs the live run.

### Follow-on: the same bug was in the recipe, so it became a shared role

Author-directed during the session: capture this so the next topic cannot
repeat it. The finding that forced the scope is that
`docs/TOPIC-RECIPES.md` § service ownership *taught* the broken order —
"`bootout` then `bootstrap` then `enable`" — so fixing only apps/backlog would
have left the recipe instructing the next daemon topic to reintroduce DOT-343.

`home/dotfiles/roles/services` now owns the unit templates (launchd agent and
systemd user unit), the convergence order and the teardown, mirroring
`roles/guards` (import_role, tasks_from routing, defaults for every parameter).
`apps/backlog` is the first caller and the proof it works on a real topic: its
two per-topic templates are deleted, not left unused, because a leftover
template is the copy a future edit updates by mistake.

The role's tests are split deliberately. Convergence is tested once, against
the role, by running its own command at throwaway labels — rendering tests
cannot catch the bug because the buggy command rendered perfectly. The topic
test now pins only the wiring (label, argv, log path, health probe, teardown
symmetry), so there is one place to be wrong about the rule rather than two.

Mutations proven on the role: reordering to the original
`bootout;bootstrap&&enable` chain fails the disabled-label convergence test and
the order property; gating `enable` behind `&&` fails both as well; dropping
`--foreground` and drifting the log path each fail the wiring tests.

One honest gap: removing the teardown *wait* survives the suite. The wait is
documented as asynchronous-bootout insurance, and it was **not reproducible**
on this host (0 failures in 25 attempts), so the README and the task comment say
that rather than claiming a race that was never observed.

`apps/backlog`'s systemd unit name changes from `backlog-daemon.service` to
`com.backlog-py.daemon.service` so both init systems share one stem. A Debian
host with the old unit needs `systemctl --user disable backlog-daemon.service`
once; no Debian host here was in that state, and the macOS run is unaffected.

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
event_id: run-ad0c62bade7340bb8153008d7d4b8a98
type: claim_task
actor: opencode-dot-343-launchctl-rc5
timestamp: '2026-11-17T17:18:41.066502Z'
result: succeeded
task_id: DOT-343
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
