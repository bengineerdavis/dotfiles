---
id: DOT-253
title: Refresh agent-skills tracker and domain configuration
status: In Progress
created_date: 2026-10-28 05:03
labels:
- documentation
priority: medium
updated_date: 2026-10-28 05:06
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The agent-skills setup already uses backlog/ and single-context domain docs, but docs/agents/issue-tracker.md still says the cutover has not landed and domain.md makes the decision store conditional on it. The maintainer confirmed backlog/, default triage labels, and single-context on 2026-10-27.

Ship:

- Mark the backlog tracker active and remove the stale TASKS.md interim guidance.
- Describe backlog/decisions/ as the current decision store.
- Leave the existing AGENTS.md Agent skills block and triage labels unchanged.

Constraints:

- Docs-only branch; no tracker or label migration.
- Do not create GitHub labels or new domain files.

Agreed with the maintainer 2026-10-27: refresh the existing setup rather than scaffolding a new one.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 docs/agents/issue-tracker.md says the cutover is complete and backlog/ is the queue of record.
- [ ] #2 docs/agents/domain.md names backlog/decisions/ as the current decision store without a cutover condition.
- [ ] #3 AGENTS.md and docs/agents/triage-labels.md are unchanged.
- [ ] #4 uv run --frozen pytest tests/docs -q passes.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
PR #95 opened 2026-10-27 for the two-doc refresh; tests/docs 13 passed and skillet Valid.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
