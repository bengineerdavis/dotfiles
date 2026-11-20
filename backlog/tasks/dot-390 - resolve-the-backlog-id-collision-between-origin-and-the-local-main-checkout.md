---
id: DOT-390
title: Resolve the backlog id collision between origin and the local main checkout
status: To Do
created_date: 2026-11-19 21:02
updated_date: 2026-11-19 21:29
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
Git-topic wrap-up, 2026-11-19:

The shared main checkout /Users/ben.davis/.local/share/chezmoi has an unresolved merge of origin/main a42039eff4c98ce05e9500d96af03425de760e84 into local main. Local main is at a3278e00381fe7245cd1260dba5adb92d43bdba8; the checkout contains many other sessions commits. Do not reset, clean, or sweep them.

The only unresolved path is backlog/tasks/dot-381 - Decide-how-copier-cat-and-redge-share-lore-knowledge-since-no-per-project-scope-config-exists.md. The incoming version adds the author ruling dated 2026-11-19, superseding the workspaces proposal with per-repo lore import in each own session. Preserve the incoming decision when the task owner resolves it.

.lore.md contains conflict markers from the interrupted merge. Do not hand-edit them; use Lore own merge/import tooling and verify knowledge by entry ID. Both versions have disjoint Lore entry IDs, so choosing one would discard entries from the other.

DOT-352 differs across local and remote main: local main has the merged close-out; the remote task file before this queue PR retained an older in-progress lease. The queue PR carries the merged close-out without the unrelated local history.

queue-backup-dot-353 at c00f2ab39ed8c520f0246883913e8106b5dbb529 remains unmerged. It contains 12 unique queue commits and must not be deleted as cleanup. DOT-353 is Done for the scanner-disable repair, not for deleting the backup.

Owned foreign dirty paths to leave alone: backlog/tasks/dot-140*, dot-343*, dot-348*, dot-349*, tests/ollama_models/test_{adopt_command,comment_preservation,rewrite_units}.py. Other sessions have been writing during the wrap-up; re-inventory before any reconciliation.

The isolated queue publication branch is agent/git-topic-queue-wrapup at .worktrees/git-topic-queue-wrapup. It is based on origin/main and contains only the task records and retro fragment for the Git-topic session.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done

<!-- DOD:BEGIN -->

<!-- DOD:END -->
