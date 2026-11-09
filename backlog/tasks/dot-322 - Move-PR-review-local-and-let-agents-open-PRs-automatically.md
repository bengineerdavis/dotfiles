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

Scope boundary (author, 2026-11-08): **push + open PR only; merge stays
human-approved.** The guard belongs on the merge, not the PR — an agent that
cannot auto-merge is safe to open PRs freely, as long as every submission is
reviewed and interrogated before merge. A tiered system to decide which changes
may even *skip* human review is later work, not this task.

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
   open/edit a PR without an author round-trip — `git push`, `gh pr create`,
   `gh pr edit` move from ask to allow — expressed in
   `home/dot_config/opencode/opencode.jsonc.tmpl` and `docs/PERMISSIONS.md`,
   with the tier test updated and seen to fail against the old rule.
2. Merge stays human-gated: an agent may run `gh pr merge`, but only after an
   explicit human approval for that PR. Auto-merge (roborev-pass + CI-green →
   merge with no human in the loop) is out of scope and belongs to the later
   tiered-review work.
3. The destructive carve-outs survive unchanged: force-push stays denied/ask,
   `gh auth` stays ask. `gh pr merge` stays ask (the prompt is the approval) or
   is paired with an explicit "only after human says go" process rule — settled
   at implementation, either way no unapproved merge.
4. The local review loop is documented: agent opens a PR → roborev reviews →
   findings fixed → the author reads the verdict and approves merge in-session.
   No new merge automation beyond the permission change.
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

Settled with the author 2026-11-08 (grilling round 1):

- **Q1 (scope):** push + open/edit PR only. No merge automation now.
- **Q2 (review location):** local — read the roborev verdict + fixes, approve
  merge in-session.
- **Q3 (merge authority):** an agent may run `gh pr merge`, but ONLY with human
  approval still required. No auto-merge.
- **Q4 (permission width):** narrow set — `git push`, `gh pr create`,
  `gh pr edit`. Force-push and `gh auth` stay denied/ask. Wider permissions
  added deliberately later, case by case.
- **Q5 (ladder coupling):** permission tier only, independent of the trust
  ladder rungs for now. The author's confidence: as long as an agent does not
  auto-merge, creating PRs is fine, provided the submission is reviewed and
  interrogated.

Author's framing (keep as the working principle): even a low-rung agent may open
PRs freely — the risk is concentrated in *merging*, not in proposing. Guard the
merge, not the PR.

**Future work (out of scope, flagged for later, NOT a task yet per author
"not now"):** a tiered system that evaluates a branch and its commits to decide
whether a change may be reviewed autonomously or requires human review/approval.
Related to, but distinct from, the DOT-208 LEDGER (which gates self-merge
promotion by streak). This DOT-322 change deliberately does not build that
tiered gate.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->