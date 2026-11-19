---
id: DOT-390
title: 'Resolve the backlog id collision between origin and the local main checkout'
status: To Do
created_date: 2026-11-19 21:02
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

**READ THIS FIRST — this task file is itself part of the problem it
describes.** The backlog-py id allocator on the shared main checkout runs
against a stale view and re-issues ids origin/main has already used. This
file was created 2026-11-19 as "DOT-389" for the collision handoff while a
DIFFERENT DOT-389 (the gita session retro, pushed to origin in cab06055's
series) already exists on origin/main. Do not trust ids issued from this
checkout until the collision below is resolved.

**The collision (measured 2026-11-19, /Users/ben.davis/.local/share/chezmoi):**

- origin/main carries (from the gita-catalogue-nesting session, pushed
  a42039ef..cab06055):
  - `dot-387 - gita-re-register-by-name-before-add-so-moves-and-ghosts-cannot-duplicate-rows.md`
  - `dot-388 - gita-a-check-fails-when-a-declared-repo-s-path-does-not-match-its-catalogue-entry.md`
  - `dot-389 - retro-capture-findings-from-the-gita-catalogue-nesting-session.md`
- the local main checkout holds UNPUSHED commits (31 ahead, incl. work parked
  on origin/preserve/dot349-handoff) that allocate the SAME ids to different
  tasks:
  - `dot-387 - Prove-whether-a-subagent-can-write-a-file-since-ours-returned-its-own-session-log.md` (9df1a609)
  - `dot-388 - Make-the-dotagents-caller-guard-find-callers-it-cannot-see-and-prove-it-still-fails.md`
  - this file as a second DOT-389

**Resolution steps for the next session (author-tier or by explicit ask):**

1. `git -C /Users/ben.davis/.local/share/chezmoi fetch origin && git log --oneline origin/main..main` — inventory the 31 local-only commits;
   separate parked-on-preserve work from genuinely unpushed work.
1. Renumber the LOCAL unpushed duplicates to the next free ids AFTER a full
   pull (`backlog-py task renumber DOT-387 <new>` per file — the CLI command
   verified absent in 2.2.0; use `git mv` + frontmatter `id:` edit, the
   mechanism DOT-249 used). Re-number so BOTH sides exist: keep origin's
   gita 387/388/389 as-is, move the local subagent/dotagents/this-file trio
   to fresh ids.
1. Commit the renumbered files + the collision resolution record on main
   (backlog carve-out), push.
1. Root-cause the allocator: backlog-py should allocate from origin/main's
   max, not the stale local view — file upstream or in the fork
   (bengineerdavis/backlog-md-py; upstream submissions FORBIDDEN).

**Do not**: create new tasks from this checkout until resolved (each one
risks another collision); renumber origin's gita tasks (they are the pushed
side and carry session evidence); sweep the parked 31 commits (they hold
other sessions' work: 131e2df6/9df1a609 are preserved on
origin/preserve/dot349-handoff, a3278e00 is on no remote).

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
