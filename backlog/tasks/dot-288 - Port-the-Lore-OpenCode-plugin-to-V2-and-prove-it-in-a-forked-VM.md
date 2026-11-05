---
id: DOT-288
title: Port the Lore OpenCode plugin to V2 and prove it in a forked VM
status: To Do
created_date: 2026-11-01 16:33
assignee:
- opencode-lore-plugin-worker
labels:
- loreai
- opencode
- upstream
- vm-tests
priority: high
references:
- https://github.com/BYK/loreai/issues/2021
- https://github.com/bengineerdavis/loreai
orchestration:
  status_key: inprogress
  lease_owner: opencode-lore-plugin-worker
  lease_expires_at: '2026-11-01T17:37:49.964479Z'
  version: 1
updated_date: 2026-11-01 16:40
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Author-authorized cross-repository execution, 2026-11-01. Build on upstream BYK/loreai main in an isolated checkout of bengineerdavis/loreai. The worker owns one branch and may commit, push to the fork, and open a pull request targeting bengineerdavis/loreai main only. Do not submit an upstream PR or contact the upstream maintainer. BYK/loreai#2021 is the existing issue and migration brief. Implement a supported OpenCode V2 plugin port, preserving the existing V1 entrypoint where the supported compatibility contract permits it. Verify more than export-shape acceptance: a disposable Debian Lima VM must load the candidate with an isolated OpenCode state, record a synthetic project-scoped session through the candidate's gateway, and read the recorded message back through Lore's supported read-only API. Report project-file and native-tool behavior separately, without claiming parity unless proven. Test no-plugin and negative cases. Reuse the existing rootless Lima/Molecule machinery; no sudo, Vagrant, live gateway, live Lore database, or host OpenCode configuration mutation. Do not edit dotfiles files or adopt the fork into the live topic. If an upstream API limitation blocks functional parity, report that boundary and open only a defensible partial PR, never a green loader-only PR. A handoff must name commits, exact test counts and commands, VM teardown evidence, remaining limitations, and review URL.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A fork branch based on current upstream main implements the supported OpenCode V2 plugin contract and retains the old host entrypoint where supportable.
- [ ] #2 A disposable Debian Lima VM proves an active V2 plugin, isolated session recording, and read-only recall of the exact test message; unproved plugin features are explicitly listed.
- [ ] #3 Negative tests show that loader failure or unavailable recording cannot be reported as success; regression tests are seen to fail before the fix.
- [ ] #4 The candidate and its VM state are torn down without touching live Lore/OpenCode state; a pull request targeting the author's fork is ready for author review.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Author refinement 2026-11-01: success is a usable OpenCode/agent setup, not Lore availability at any cost. The candidate must demonstrate a supported failure path in which an unavailable plugin or gateway cannot prevent the host agent reaching its configured upstream. No blanket gateway route may silently become a single point of failure. Treat this fork as an opt-in beta/configuration trial, not live adoption. The reusable container-to-VM beta process for ordinary topics is a separate requirements effort; do not expand this ticket into that infrastructure build.

Author correction later on 2026-11-01: Lore is intended to become required memory infrastructure, not optional forever. The immediate defect is the host agent's inability to tolerate a plugin failure. Temporary fallback is recovery only, not the desired architecture. Keep the Lore V2 port as this task's primary outcome; investigate OpenCode resilience separately rather than weakening the required integration. Do not assume a plugin-load error necessarily prevents the whole agent from working without direct evidence.
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
event_id: run-2983d353738c448c8a9099e36d676654
type: claim_task
actor: opencode-lore-plugin-worker
timestamp: '2026-11-01T16:37:49.964545Z'
result: succeeded
task_id: DOT-288
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
