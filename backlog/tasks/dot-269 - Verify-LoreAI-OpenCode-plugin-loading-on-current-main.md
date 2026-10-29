---
id: DOT-269
title: Verify LoreAI OpenCode plugin loading on current main
status: In Progress
created_date: 2026-10-29 08:25
assignee:
- opencode
labels:
- loreai
- opencode
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rebase PR #89 onto current main with the home/ payload layout. Verify that the LoreAI topic distinguishes registered, installed, and actually loaded OpenCode plugin states, including a successfully loaded plugin row. Keep upstream V1-plugin compatibility and live machine remediation separate. Work in .worktrees/loreai-plugin-verify on branch agent/loreai_plugin_verify.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 PR #89 rebases onto current main without restoring the old dotfiles payload path.
- [ ] #2 Focused tests prove both a broken plugin state and a successfully loaded plugin state, with mutation evidence for new tests.
- [ ] #3 The topic verification evidence is current and names any unverified live-machine or upstream limitations.
- [ ] #4 The updated PR is pushed and ready for human review; no chezmoi apply or host service change is performed.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Current main and focused plugin verification evidence are recorded on the updated PR; no unsupported claim that the upstream plugin now loads.
<!-- DOD:END -->
