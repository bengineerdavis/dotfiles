---
id: TASK-244
title: 'loreai: verify the opencode plugin loads, not just registers'
status: To Do
created_date: 2026-10-28 00:04
labels:
- loreai
priority: medium
references:
- https://github.com/bengineerdavis/dotfiles/pull/89
modified_files:
- dotfiles/apps/loreai/tasks/agents/opencode.yaml
- dotfiles/apps/loreai/README.md
- changelog.d/20261027_131500_bengineerdavis_loreai_opencode_plugin_verify.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Measured 2026-10-27: the deployed config listed @loreai/opencode while the shared opencode server's in-process auto-install failed for hours (protocol errors, then lock-timeout collisions, in the opencode server log), and once installed the v2 loader still rejected 0.40.0's pre-v2 function-shaped default export — so the topic's config-grep verification reported a working gateway that was not there.

Ship:

- apps/loreai/tasks/agents/opencode.yaml verifies registered / installed / loading via `opencode plugin list` plus the server log's last failure line for the plugin
- registered-but-broken states raise: a wedged install fails the run with the fix commands; a loader rejection raises red without blocking (ignore_errors, recap ignored=1)
- README.md and a changelog.d fragment record the measurement

Constraints:

- warn-not-fail only for the not-registered state (chezmoi render order is not this topic's to enforce); broken states raise (author ruling 2026-10-27)
- verify before commit: ansible-playbook --syntax-check and --check --tags provision (TOPICS.md)
- commit by path, `<scope>: <imperative>` subject (CONTRIBUTING.md)

Decision record: author ruling 2026-10-27 — broken plugin states raise, escalation matched to who can fix them; the load fix itself is upstream (BYK/loreai).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The verify task reads `opencode plugin list` and the server log's last failure line for @loreai/opencode, not just the deployed-config grep.
- [ ] #2 Under `--check --tags provision` on a machine whose plugin is registered-but-not-loading, the loader rejection surfaces as FAILED! with failed=0 and ignored=1.
- [ ] #3 README.md and a changelog.d fragment record the 2026-10-27 measurement.
- [ ] #4 `ansible-playbook apps/loreai/playbook.yaml --syntax-check` exits 0.
- [ ] #5 `ansible-playbook apps/loreai/playbook.yaml --check --tags provision` ends failed=0 changed=0.
- [ ] #6 PR open: bengineerdavis/dotfiles#89 from agent/loreai_plugin_verify.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Incident trace: opencode server log run=9151fedc, error refs err_9fd444e1 (LockTimeoutError) and err_9aed68f7 (NpmInstallFailedError ERR_INVALID_PROTOCOL). Fresh-process `opencode plugin add` installed the package the wedged server could not.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
