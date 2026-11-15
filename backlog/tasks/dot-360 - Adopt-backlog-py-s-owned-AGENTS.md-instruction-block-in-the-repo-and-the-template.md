---
id: DOT-360
title: Adopt backlog-py's owned AGENTS.md instruction block in the repo and the template
status: To Do
created_date: 2026-11-15 20:21
priority: high
updated_date: 2026-11-15 20:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
backlog-py ships `agents --update-instructions`, which maintains a
marker-delimited block (`<!-- BACKLOG_MD_INSTRUCTIONS_START/END -->`) in
AGENTS.md, CLAUDE.md, GEMINI.md and .github/copilot-instructions.md
(core/agents.py:11-18). docs/BACKLOG-MIGRATION.md:127 documents it as the
mechanism and states house sections stay outside the markers. Measured
2026-11-15: `grep -c BACKLOG_MD_INSTRUCTIONS AGENTS.md` returns 0 here, and
agentic-project-template carries hand-written prose instead
(fragments/agents-md-backlog-section.md, fragments/tools/backlog-py/agents.md).
Agents therefore read house descriptions of the store rather than the store's
own maintained instructions, and the two drift: this session asserted a
`task show` verb that does not exist while `task --help` documents
`task <id>`.

Ship:

- The owned block present in this repo's AGENTS.md, house sections outside the
  markers and unchanged
- The template emitting the same block at stamp time rather than hand-written
  prose
- A check that fails when the block is missing or has drifted from the
  installed backlog-py version
- The boundary written down: what the owned block covers, what house sections
  own, and which wins when they disagree

Constraints:

- Run the CLI to write the block; never hand-copy its text
- Resolve conflicts with house rules explicitly — the queue-specific rules the
  migration removed are not re-added (docs/BACKLOG-MIGRATION.md:127)
- The block lands in the same change as the boundary note, so no session reads
  two contradictory tracker conventions
- Template work composes additively and never clobbers a project's existing
  AGENTS.md (agentic-project-template layering contract, 2026-11-09)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 backlog-py agents --update-instructions has written the owned block into this repo's AGENTS.md
- [ ] #2 House sections sit outside the markers and are unchanged by the update
- [ ] #3 The template emits the owned block at stamp time instead of hand-written backlog prose
- [ ] #4 A check fails when the block is absent or drifted from the installed backlog-py version
- [ ] #5 The boundary between owned block and house sections is written down, naming which wins on conflict
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
