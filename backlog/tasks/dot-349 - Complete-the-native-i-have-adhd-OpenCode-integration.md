---
id: DOT-349
title: Complete the native i-have-adhd OpenCode integration
status: To Do
created_date: 2026-11-10 20:55
dependencies:
- DOT-348
updated_date: 2026-11-18 07:10
orchestration:
  status_key: inprogress
  lease_owner: opencode-dot349
  lease_expires_at: '2026-11-18T05:11:55.206230Z'
  version: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The global dotagents source installs i-have-adhd's canonical skill but does not establish the complete native OpenCode integration documented upstream. dotagents 3.4.0 links plugin skills into OpenCode; its documentation does not claim to project .opencode/plugins/*.mjs or OpenCode commands.

Ship:

- Test the installed dotagents projections for i-have-adhd in isolated HOME fixtures for every configured runtime, reporting passed, failed, and unsupported behavior explicitly.
- Add the native i-have-adhd OpenCode plugin, /i-have-adhd command, and matching teardown through apps/opencode, leaving always-on disabled unless the author separately enables it.
- Prepare a narrowly scoped upstream dotagents installation proposal from a fork, or document why the measured integration needs no upstream change.
- Record all verified integration findings and references in the owning topics.

Constraints:

- Do not fork to change the canonical skill rules. Use the existing upstream source.
- Upstream asks that new integrations be discussed in an issue first. Publication to an issue or PR requires separate explicit author approval.
- The OpenCode adapter belongs to apps/opencode; shared skill declarations remain in apps/dotagents.
- Never enable the always-on hook implicitly or run chezmoi apply without author approval.

Decision record: Approved by the author 2026-11-10 as the queued B follow-up to the core dotagents installation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Isolated projection tests report each configured runtime as passed, failed, or explicitly unsupported; no skip counts as a pass.
- [ ] #2 The native OpenCode plugin and command load in an isolated configuration directory, with tests proving both activation and opt-out behavior.
- [ ] #3 The always-on flag remains absent and no always-on content is injected by default.
- [ ] #4 The OpenCode topic teardown removes exactly the adapter state it creates.
- [ ] #5 The upstream contribution decision and measured evidence are recorded, and no upstream issue or PR is published without explicit approval.
- [ ] #6 The owning topic docs contain the verified findings and authoritative upstream references.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
2026-11-17 progress (branch agent/dot-349, commit 2848cf71): measured that dotagents 3.4.0 installs the plugin's FULL upstream tree including .opencode/plugins/i-have-adhd.mjs but projects only skill links into OpenCode — so no vendored clone is needed and option (a) reduced to a 38-line loader rather than a third-party tree. OpenCode 2.3.1 on this box; the plugin exports setup(ctx), the V2 API, so the Lore V1-API failure does not repeat here. Verified OpenCode auto-discovers ~/.config/opencode/plugins/*.js via `opencode plugin list`, which lists herdr-agent-state.js as a loaded local plugin — so the loader needs no plugins-array entry in opencode.jsonc. Shipped: templates/i-have-adhd-loader.js.j2 (re-exports upstream, resolves its dependency from os.homedir() at load time — no machine-specific literal), install.yaml probe-then-write with the fix named (run the dotagents topic), remove.yaml teardown of loader + flag only, and the always-on flag file by author request 2026-11-17 (upstream's alwaysOnInjection() returns null without it, so the loader alone is a no-op). 16 tests in tests/topics/test_opencode_adhd_loader.py, 10 mutations each seen failing. Gate: full suite 3 failed / 1720 passed / 6 skipped, all 3 pre-existing on main (2 lore rules + test_guard_wiring dotagents-stderr, the latter confirmed failing at HEAD~1 too). Ruff clean, skillet Valid. REMAINING before the task is done: push, PR, author merge, then chezmoi apply + run-role opencode from main and confirm the hook injects. Deliberately NOT done: upstream dotagents proposal (task's third Ship bullet) — publication needs separate author approval per its Constraints.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Measured 2026-11-15 in isolated dotagents 3.4.0 fixtures: targeting only OpenCode installs ~/.agents/plugins/i-have-adhd and links ~/.config/opencode/skills/i-have-adhd to the canonical skill. It creates no .opencode plugin or command output. The upstream .opencode/plugins/i-have-adhd.mjs setup hook registers a context hook on load; always-on injection remains flag-gated. B must prove the native setup hook and command explicitly; an installed skill link is not evidence that B is complete.

Author ruling 2026-11-15: A stays skill-only for OpenCode. B retains the setup hook and command work, with always-on opt-in.
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
event_id: run-3008b671dc4e47398837e15fb9dc35dd
type: claim_task
actor: opencode-dot349
timestamp: '2026-11-18T04:11:55.206286Z'
result: succeeded
task_id: DOT-349
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
