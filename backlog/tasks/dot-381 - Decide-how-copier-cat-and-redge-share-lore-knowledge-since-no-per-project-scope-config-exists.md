---
id: DOT-381
title: Decide how copier-cat and redge share lore knowledge, since no per-project
  scope config exists
status: To Do
created_date: 2026-11-18 21:42
updated_date: 2026-11-18 21:43
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

The author asked for copier-cat and redge to share lore knowledge. Investigating
the surfaces shows there is nothing to edit: lore has **no per-project config
file at all**. There is no `.lore.toml`, no scope key in the project row, and no
`lore share` command. So this is a decision, not a config edit.

What actually exists (verified 2026-11-18, lore v0.40.0):

- **`projects` table has no scope/sharing column.** Columns are id, path, name,
  created_at, git_remote, last_import_at, last_decay_at, last_refcheck_at,
  scope_id, promotion_policy, tenant_id. `scope_id` exists but is empty on all
  21 project rows and there is no scope UI for it.
- **Sharing is hosted-only.** `lore sync status` reports "disabled / not logged
  in / encryption off". `lore login` + `lore sync enable` is the team path, and
  the `scopes` / `team_knowledge` / `org_members` tables are all empty locally.
  Turning that on sends project knowledge to a hosted service — a trust-boundary
  decision the author owns, not a mechanical config change.
- **The only local cross-project mechanism is `knowledge.cross_project`**, a
  per-row boolean. 149 of 4187 rows are flagged; the flagged titles are
  general preferences and standards (e.g. "Prefer mise-managed tools over brew",
  "Responses in English only"), not project-specific architecture. Nothing
  writes that column except lore's own promotion logic.
- **redge has no project row at all.** It has never been opened in a lore
  session on this machine, so it contributes and receives nothing today. Its
  knowledge would start accumulating only after a session runs with it as cwd.

The decision: pick one of —

(a) **Hosted sync** (`lore login`, `lore sync enable`) — real sharing, but
knowledge leaves the machine and redge must first be registered by a
session. Cost: a trust-boundary decision plus a paid/hosted dependency.
(b) **Local promotion** — flag selected rows `cross_project` so both projects
can recall them. Cheap and stays local, but there is no CLI to set the flag;
it would mean writing to lore's DB or finding the promotion path in
upstream source.
(c) **Dependency, not memory sharing** — copier-cat records its redge-relevant
findings in-tree (the existing `backlog/docs/` pattern), and redge reads
them as research input. No lore coupling at all.

Recommendation to evaluate first: (c), because the material that needs to cross
the boundary right now is a small set of design findings, not a standing memory
stream, and (c) survives a machine rebuild while (a) and (b) depend on state
outside git.

Ship:

- A decision record choosing (a), (b), or (c), with the trust-boundary
  consequence stated explicitly if the answer is (a)
- If (c): the redge-relevant gita findings written where redge can consume them,
  citing the source decision rather than duplicating its prose
- If (a) or (b): the mechanism documented and verified end-to-end — a fact
  learned in copier-cat is recallable from redge, demonstrated rather than
  assumed
- redge registered as a lore project (requires a session in that repo, or a
  direct row insert; the former is the supported path)

Constraints:

- Never enable hosted sync without the author's explicit consent — it moves
  knowledge off the machine and is a one-way trust decision
- Do not hand-write lore's DB as the first resort; if (b) is chosen, find the
  supported promotion path in upstream source first
- redge is third-party-adjacent (Fair Source, FSL-1.1-MIT) — the decision must
  state whether copier-cat's knowledge crossing into it is acceptable at all

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 A decision record states which sharing mechanism is chosen (hosted sync, local cross_project promotion, or in-tree dependency) and gives the reason
- [ ] #2 The trust-boundary consequence is stated explicitly when hosted sync is chosen
- [ ] #3 If in-tree dependency is chosen: redge-relevant gita findings exist where redge can consume them, citing the source decision rather than duplicating its prose
- [ ] #4 If hosted sync or local promotion is chosen: recallability is demonstrated end-to-end, not assumed — a fact from copier-cat is retrievable from redge
- [ ] #5 redge appears as a lore project or the task records why it remains unregistered
- [ ] #6 The board lists DOT-381 with the full description: uvx --from backlog-md-py backlog-py board
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
