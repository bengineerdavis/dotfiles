---
id: DOT-277
title: Make mise upgrade results readable and resilient to Ansible controller reinstallation
status: To Do
created_date: 2026-10-30 06:24
labels:
- mise
- ansible
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
During the 2026-10-29 ./update.sh run, mise upgraded 12 tools, then reinstalled pipx:ansible as part of its Python-3.14 pipx refresh even though the command excluded pipx:ansible. Ansible 2.21.5 could not deserialize the completed command result (Unknown profile name module_legacy_m2c); changed_when then failed because the registered result had no stdout. The raw module_stdout contains valid JSON with rc=0. mise also warned that whisperx 3.8.5 could not reinstall because torch 2.8 has no cp314 wheel, but exited 0, so the existing rc/stderr failure detector missed it. Fix the public upgrade path so controller refreshes cannot invalidate in-flight Ansible results where avoidable, surviving raw results are handled safely, per-tool warnings are reported concisely, and huge escaped JSON/YAML blobs are not dumped during normal upgrades. Do not run a real-host playbook or chezmoi apply; prove with synthetic localhost plays and mutation checks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A synthetic Ansible 2.21 result containing only module_stdout JSON is recovered without a changed_when error and with correct changed/rc/stdout/stderr fields
- [ ] #2 A normal upgrade does not dump full command output; changed tools and actionable failures are printed with real newlines in a bounded report
- [ ] #3 mise WARN failed-to-reinstall output with rc=0 is surfaced as a tool failure rather than silently treated as success
- [ ] #4 The test fails against the old upgrade task (mutation recorded), then passes after the fix; focused and full suites pass
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
