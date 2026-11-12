---
id: DOT-355
title: Review how backlog/ is committed from parallel worktrees
status: To Do
created_date: 2026-11-12 22:34
labels:
- backlog
- git
- worktrees
updated_date: 2026-11-12 22:34
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Why: a backlog commit made with `git commit -o` swept another
session's task file into it. The file was not a timestamp bump — it carried their
real implementation notes and final summary for DOT-140. Caught before it left
the machine, but the mechanism is repeatable and the policy does not cover it.

What happened, measured 2026-11-12: `git commit -o <dot-354 task file>` in the
main checkout staged only the named path, but backlog-py had already rewritten a
neighbouring task file on disk. The named path was fine; the problem is that the
index and the working tree are shared with a session that is editing other task
files, so any command that touches more than the one path can carry their work.
A second, separate cause: the same commit's first attempt also picked up a
neighbouring file because `git commit -o` on an UNTRACKED path errors
(`pathspec ... did not match any file(s) known to git`), so the file had to be
`git add`-ed first — and `git add` is what takes the whole path, not a
selection of its hunks.

The relevant rules, verified against this repo:

- `docs/BACKLOG-MIGRATION.md` § Queue commit policy (author ruling 2026-10-23):
  "`backlog/` writes go straight to main. Task create/edit/claim commits are
  coordination overhead ... Code, docs, and policy stay branched." So backlog
  commits are expected to happen on main, from whichever checkout.
- `backlog/config.yml`: `autoCommit: false`, `remoteOperations: false`, and a
  house rule (`.lore.md`, BACKLOG-MIGRATION.md:85-86) that "the tool never
  commits and never reaches the network on its own". Confirmed: no `--commit`
  flag exists on `backlog-py task`, and `backlog-py config list` shows both
  false.
- `backlog-py task create --help` offers no staging or commit option; the tool
  writes files and leaves git to the human. That is deliberate, not a gap.

So the tool is behaving as designed. The open question is the human-side
mechanism for committing one task file while another session has the tree
dirty — and whether the correct answer is a command form, a worktree
convention, or a change to the policy.

Ship: a written answer to "what is the correct or sufficient way to commit
`backlog/` writes when other worktrees have the tree dirty", backed by
backlog-py's own docs and CLI help rather than recollection, and applied to the
next backlog commit.

Constraints:
- Do not change `autoCommit` to true. The house rule that the tool never commits
  is a deliberate decision, and a tool that commits would race the same tree.
- `git add` of a specific path is not sufficient protection: the danger is a
  path the command does not name, not hunks within a named path.
- Any answer must work when the main checkout is dirty, because that is the
  normal state (12 files from another session at the time of writing).

Open questions:
- Does `backlog-py` write neighbouring task files on every edit (re-index), or
  only on some operations? The 2026-11-12 case showed DOT-140 rewritten while
  DOT-354 was created; that is the same class as the queue-integrity findings.
- Is a dedicated backlog worktree viable, given the policy says writes go
  straight to main and `checkActiveBranches` reads branch tips?
- Would `git commit --only <path>` (the long form of `-o`) with a clean index
  be sufficient, or does it still take a dirty neighbour?
- Does `backlog-py doctor` or a prek hook already detect a task file modified
  by another session's write?

Sources to read before answering: `backlog-py task --help`,
`backlog-py config list`, `docs/BACKLOG-MIGRATION.md` § Queue commit policy,
`docs/WORKTREES.md`, and the queue-integrity hook in `prek.toml`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The answer cites backlog-py's own CLI help and docs for the `autoCommit` / no-commit-by-tool behaviour, not recollection.
- [ ] #2 It states plainly whether `git commit -o <path>` is sufficient from a dirty shared checkout, with the evidence that settles it.
- [ ] #3 It gives one recommended mechanism for committing a backlog write while another session has the tree dirty, and names the alternative it rejected and why.
- [ ] #4 The recommended mechanism is exercised on the next backlog commit, and the result recorded here.
- [ ] #5 If the answer is a policy change (e.g. a dedicated backlog worktree), the change lands in `docs/BACKLOG-MIGRATION.md` in the same PR rather than as a note.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-11-12 — measured answer to the main question, on a live dirty tree
(8 other task files modified by a concurrent session, including DOT-140):

`git commit -o <path>` IS sufficient, given two conditions:
1. the path is already tracked OR staged first (an untracked path makes
   `-o` error with "pathspec ... did not match any file(s) known to git");
2. the index holds nothing else for that commit.

Verified: staged one new task file, ran `git commit -o <that file>` with 9
dirty neighbours present, result was 1 file changed / 103 insertions, and every
neighbour stayed dirty afterwards. DOT-140's uncommitted notes survived intact.

So the original incident's cause was NOT `-o` leaking neighbours. It was the
`git add` needed to make an untracked path committable, combined with the file
already having been rewritten on disk by backlog-py's re-index — the second
attempt at that commit picked up DOT-140 because DOT-140 was dirty at the moment
`git add` ran on a *different* path... worth re-checking whether that is exactly
what happened, but the safe procedure is clear either way:

  git add <the one task file>
  git diff --cached --name-only   # assert exactly one path
  git commit -o <that same path>

The `git diff --cached --name-only` assertion is the cheap guard: it makes a
sweep visible before the commit rather than after.

Alternative rejected: making backlog-py commit for you (`autoCommit: true`).
It violates the house rule that the tool never commits, and a tool committing
would race the same dirty tree with less visibility, not more.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
