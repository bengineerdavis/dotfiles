---
id: TASK-218
title: Make `rerere.enabled` and `merge.conflictstyle=zdiff3` portable
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Make `rerere.enabled` and `merge.conflictstyle=zdiff3` portable.** Both are
  set on this machine's `.git/config` for the chezmoi repo (2026-09-23) and reach
  every worktree, because worktrees share the common `.git/config`. They do not
  travel to another machine. `rerere` records a conflict resolution and replays
  it when the same conflict reappears, which is worth far more under the
  one-writer-per-worktree model than it was before: a tree merge surfaces the
  same conflict once per level, and resolving it three times by hand is three
  chances to resolve it differently. `zdiff3` adds the common ancestor to
  conflict markers, which is what distinguishes "both sides added a line, keep
  both and renumber" from "both sides renamed the same line, pick one" — the
  markers are identical without it, and the wrong reading silently deletes a
  value other code already branches on.

  Blocked on a decision, not on work: there is no chezmoi-managed git config and
  no `apps/git` topic, so this needs either adopting the unmanaged
  `~/.gitconfig` into chezmoi or creating a git topic. An agent cannot do the
  first — `~/.gitconfig` is outside the agent sandbox, so it cannot be read, and
  `spec.md` § Data forbids committing employer-identifying strings sight unseen.
  Either the author adopts it, or the sandbox grants read access, or the topic
  route is chosen. Done when both settings land on a second machine without
  being typed there. Note this is a deployed-tree path, so it is PR-and-review
  either way per `AGENTS.md` § Merge gates.

  **Done 2026-09-23** in `d9b15a1` and `cf30fb7`, on branch
  `skill-trust-foreign-buckets`. The author supplied `~/.gitconfig`, so the
  adoption route was taken: it is now `dot_gitconfig.tmpl`, with its three
  hardcoded `/Users/ben.davis` paths resolved through `.chezmoi.homeDir` —
  they would have failed silently on Linux. Two questions were left open
  rather than decided quietly: `user.email` is a personal address that will
  follow this file onto a work machine, and the empty-named `[mergetool ""]`
  and `[difftool ""]` sections look vestigial, their `cmd` lines starting at
  `"$LOCAL"` where a program name should be. Still PR-and-review before it
  merges, being a deployed-tree path.

  **Both since resolved on main:** the identity now prompts through
  `promptStringOnce` (`gitconfig: parameterize the user identity`), and the
  empty-named mergetool/difftool sections were confirmed dead and deleted.
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
