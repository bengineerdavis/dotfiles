---
id: DOT-304
title: Revisit the roborev-review skill's --wait default — a blocking wait that outlives
  its shell
status: To Do
created_date: 2026-11-07 21:23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Author ruling 2026-11-07: keep the roborev-review skill's --wait default AS IS for now ('I want roborev reviews synced if we can help it'); revisit only if the friction recurs. Captured friction from the DOT-73 session (measured 2026-11-04): (1) --wait hit the 900s shell timeout and the wait loop died mid-poll (job 373) — the daemon-side job survived, but the skill text offers no recovery path; (2) the roborev daemon restarted 3x mid-wait (socket connection refused; the MCP server caches the pre-restart socket path while the CLI re-discovers); (3) the misfire sequence around the dead waits — review jobs 363 and 372 enqueued for main-checkout HEADs because fresh shells start in the main checkout — cost two wrong-commit reviews. Root cause shared by all three: a blocking wait that outlives its shell. Reopen trigger: any recurrence of a lost --wait, a stale MCP socket after a daemon restart, or a wrong-tree enqueued review. The resilient pattern, if reopened: record the job ID, then poll roborev_list_jobs (or roborev list) until done. NOTE: the wrong-tree half is owned separately — agent-harness cwd pinning proposal drafted on the worktrunk fork (~/code/forks/worktrunk/PROPOSAL-agent-harness-cwd.md), not posted upstream.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
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
