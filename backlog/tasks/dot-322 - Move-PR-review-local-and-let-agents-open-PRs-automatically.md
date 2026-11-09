---
id: DOT-322
title: Move PR review local and let agents open PRs automatically
status: To Do
created_date: 2026-11-08 20:05
labels:
- process
- permissions
- trust-ladder
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The author wants agent PRs to be created and reviewed without leaving his
session or local terminal. Two parts, one goal:

1. **Let agents open PRs automatically** — relax the `gh pr create` / `git push`
   ask-tier so a session can push a branch and open a PR without an author
   round-trip for the mechanical step.
2. **Move PR review local** — surface review/approve/merge inside the repo
   (roborev + a local gate) so the author does not review, approve, and merge
   on github.com outside his session.

The parts are one task because agent PR automation is pointless without a local
review step to catch them — automating the push without localizing the review
just moves the human bottleneck to a web tab.

Today the work is blocked at three points, none of which are the trust ladder
(which already grants "commit to a branch and open a PR" at rung 1, and
self-merge docs/tests at rung 2):

- `gh pr create` / `gh pr edit` / `gh pr merge` and `git push` have no explicit
  permission rule, so they fall through to the `shell *` ask catch-all in
  `home/dot_config/opencode/opencode.jsonc.tmpl` (the v2 permissions array).
  `docs/PERMISSIONS.md` allows read-only `gh` (`list`/`view`/`status`) but keeps
  the write forms at ask.
- review happens on GitHub; roborev is the local review surface but is
  review-only — it does not merge.
- merge is human-only (`gh pr merge`).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
1. A repo rules change lands (separate PR) that lets an agent push a branch and
   open a PR without an author round-trip, with the permission change expressed
   in `home/dot_config/opencode/opencode.jsonc.tmpl` (or `docs/PERMISSIONS.md`
   and its tier tests) and proven by a tier test that fails when the rule is
   absent.
2. The local review step is defined: after an agent opens a PR, roborev (or an
   equivalent local gate) reviews it and the author is offered merge inside the
   session, so approve/merge no longer requires leaving the terminal.
3. The change records why each permission widened, and keeps the existing
   destructive carve-outs (force-push stays denied/ask, `gh auth` stays ask —
   `docs/PERMISSIONS.md`).
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Cross-references for the implementer:

- **Trust ladder** — `docs/TRUST-LADDER.md`: rung 1 already grants "commit to a
  branch and open a PR" (nothing reaches main unreviewed); rung 2 self-merges
  docs/tests; rung 3 self-merges code in a named blast radius; rung 4 unattended.
  Promotion needs the ledger (DOT-208, still unbuilt), so agents start at rung 0.
  The permission tier is the actual blocker, not the ladder policy.
- **Permission source** — `home/dot_config/opencode/opencode.jsonc.tmpl`
  lines ~55-133: the v2 permissions array (ordered, LAST match wins, catch-alls
  first). `shell *` ask is line 56; there is no `gh` rule, so `gh pr create`
  etc. fall through to ask.
- **gh tier** — `docs/PERMISSIONS.md` lines ~67-71: read-only `gh` allowed
  (`list`/`view`/`status`), `gh api` GET-only, `gh auth` stays ask. Line ~74:
  Claude Code has the worktree carve-out but not the `gh` one.
- **Merge gates** — `AGENTS.md` § Merge gates: docs-only diffs self-mergeable;
  other diffs need full suite + mutation + hazard check; policy/egress/deployed
  always PR + human review. Any local auto-merge must not weaken the
  "policy/deployed always human review" clause.
- **Existing local review surface** — roborev MCP + the `/roborev-review-branch`
  skill: enqueue, poll `roborev_list_jobs`, read verdict. Review-only today.

Open design questions to settle during grilling (not pre-answered here): whether
"open a PR" should be allow-tier for a named set of subcommands (leaving
force-push and `gh auth` ask), whether merge is ever local/automatic or stays a
human confirmation, and whether this couples to DOT-208 (LEDGER) as the gate
that would otherwise promote an agent to self-merge.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->