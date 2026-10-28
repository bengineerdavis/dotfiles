---
id: DOT-250
title: Fix or route around the claude-code roborev reviewer's API 400 (malformed MCP
  tool schema)
status: To Do
created_date: 2026-10-28 01:23
labels:
- queue-integrity
ordinal: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The claude-code roborev reviewer dies on every attempt with API Error 400: tools.48.custom.input_schema.type: Field required — one of the MCP servers exposed to the reviewer (roborev's own MCP or backlog-py-mcp) emits a tool schema missing the input_schema.type field, which claude-code's API rejects. Observed 2026-10-27 reviewing agent/dot-prefix-docs (job 35 also never persisted — the roborev daemon was down, so the enqueued job was lost; the local --local review mode surfaced the error). The opencode reviewer works and is the working route until fixed. Fixes to evaluate: make the offending MCP server emit a complete schema, exclude the broken server from the reviewer's context, or pin roborev to run reviews daemonless. Legacy: found during PR #87's review.
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
