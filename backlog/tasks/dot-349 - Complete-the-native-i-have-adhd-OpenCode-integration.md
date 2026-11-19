---
id: DOT-349
title: Complete the native i-have-adhd OpenCode integration
status: To Do
created_date: 2026-11-10 20:55
dependencies:
- DOT-348
updated_date: 2026-11-16 01:17
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
