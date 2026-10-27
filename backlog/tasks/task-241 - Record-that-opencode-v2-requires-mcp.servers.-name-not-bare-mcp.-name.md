---
id: TASK-241
title: Record that opencode v2 requires mcp.servers.<name>, not bare mcp.<name>
status: Done
created_date: 2026-10-27 20:21
updated_date: 2026-10-27 20:27
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2026-10-22 roborev MCP adoption stored the block as mcp.servers.roborev; a local commit later 'fixed' it to bare mcp.roborev, which is the deprecated shape in opencode v2.1.4 (schema: mcp.servers.additionalProperties; bare mcp.<name> is marked deprecated). Record the requirement in apps/roborev's CHANGELOG known_issues so the next reader does not repeat the inversion.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 apps/roborev/CHANGELOG.md known_issues states that mcp.servers.<name> is required in opencode v2 and bare mcp.<name> is deprecated.
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
