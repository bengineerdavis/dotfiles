---
id: DOT-357
title: Retire a decision and thin its AGENTS.md rule when its remediation tasks are
  done
status: To Do
created_date: 2026-11-15 06:41
references:
- backlog/decisions/decision-3 - VM-verify-config-and-symlink-deployments-before-apply-merge-and-PR-gates.md
updated_date: 2026-11-15 06:42
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Capture works and retirement does not. decision-3 item 4 rules that incidents
become post-mortems with linked remediation tasks, and the `references:`
frontmatter field already carries that link on seven tasks (DOT-271 through
DOT-276, DOT-289). Nothing closes the loop: when the remediation lands, the
decision stays `proposed` and the rule it produced stays in AGENTS.md with its
forensics inline. Measured 2026-11-12: AGENTS.md is 1,063 lines carrying 24
dated `measured 20xx-xx-xx` entries and 5 cited commit SHAs, because every
retro appends and nothing retires. The file is not short of a home for rules —
it already links 19 of the 31 docs/ files across 33 references — so the growth
is unretired evidence, not missing structure.

Ship:

- A resolution condition on decision records: a decision is resolvable when
  every task carrying its `references:` has reached Done
- A check that reports resolvable decisions by walking `references:` and
  reading task statuses
- The thinning rule written down: on resolution the AGENTS.md entry collapses
  to the imperative rule plus one link to the decision, and the measured
  evidence stays in the decision record
- decision-3 itself run through the procedure as the worked example

Constraints:

- Separate the rule from its evidence rather than deleting either: `.lore.md`
  keeps the lesson independently, and the decision keeps the forensics
- No new record type — `decision` already holds post-mortems and three of the
  four existing decisions are ordinary ADRs, so incident is a subtype
  distinguished by its Context, not a sibling of task
- Resolution is reported, never applied automatically: thinning AGENTS.md is a
  judgement edit to the most-read file in the repo
- DOT-275 gates the capture half of this flow, not this half; retirement can be
  defined before "what counts as an incident" is settled

Per decision-3 item 4 (2026-10-29): incidents are captured as decisions with
linked remediation tasks so the failure classes stay visible after the session
ends.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A decision record carries a resolution condition: resolvable when every task referencing it is Done
- [ ] #2 A check walks references: across tasks and reports which decisions are resolvable
- [ ] #3 The thinning rule is written down: resolved decision's AGENTS.md entry collapses to the imperative rule plus one link, evidence stays in the decision
- [ ] #4 decision-3 is run through the procedure as the worked example
- [ ] #5 Resolution is reported, never auto-applied to AGENTS.md
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
