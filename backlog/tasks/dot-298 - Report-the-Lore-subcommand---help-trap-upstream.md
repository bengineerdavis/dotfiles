---
id: DOT-298
title: Report the Lore subcommand --help trap upstream
status: To Do
created_date: 2026-11-07 17:21
labels:
- loreai
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
lore 0.40.0 parses --help only at the top level. Passed to a subcommand it falls through to the normal argument parser, and the outcome depends on the command:

- lore setup --help EXECUTES setup (rewrites agent configs)
- lore data export --help EXECUTES the export (rewrites .lore.md)
- lore data list --help prints 'Unknown type (none)' then runs
- lore recall --help prints 'Unknown command' and EXITS 0

The last case is the worst shape: a failed invocation reports success, so a caller checking the exit status sees a clean run that did nothing.

lore help is the real help command and documents every subcommand. lore doctor and lore setup status are the read-only inspections.

Measured 2026-11-07, bitten twice in one session: the first run reconfigured every agent, the second rewrote .lore.md on main. The local mitigation shipped in PR #135 (README troubleshooting entry); this task is the upstream report.
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
