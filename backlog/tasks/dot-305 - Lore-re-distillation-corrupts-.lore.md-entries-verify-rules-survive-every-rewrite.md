---
id: DOT-305
title: Lore re-distillation corrupts .lore.md entries — verify rules survive every
  rewrite
status: To Do
created_date: 2026-11-07 22:16
orchestration:
  status_key: todo
  version: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two consecutive roborev reviews of agent/retro-docs (jobs 463 and 479) failed on .lore.md defects that the Lore daemon's own re-distillation produced or aggravated. Measured 2026-11-07: (1) title/body swap — entry 01a18498 ('uv run without --frozen...') carried unrelated chezmoi -S content, deleting the uv safety rule; the 21:40 heal restored it but SWAPPED a second entry (389: 'Merge PR queue: stacked-PR stranding' now carries the inline-Python-batching body, and the stacked-PR procedure is nowhere in the file). (2) Deleted-correct-entry + false trap — the requires_map entry ('skip the removal when requires_map undefined') matches remove.yaml exactly (uninstall gated on index_available; debug explains the skip; docs/TOPICS.md:146-149 mandates it: 'Undefined means unproven, not unshared — skip the removal'), yet the heal deleted it and wrote a trap entry claiming it contradicted remove.yaml. The first review's 'aborts with an explicit error' reading was ALSO wrong — verified against remove.yaml:18-22,30-48. (3) Wrong pointer — codex entry (line 58) cites decision-2 while naming decision-4 (both files exist). Root cause: the daemon rewrites the file on its own schedule; a hand-fix or capture commit races the next rewrite, and each heal can mint new defects. Fix direction: this is upstream behavior — report to BYK/loreai (DOT-298 pattern). Until it settles, treat .lore.md commits as captures-only (never hand-edit content), re-verify load-bearing rules survive each rewrite, and keep reviews green on the non-.lore.md payload. Interim guard: the drift test pattern (tests/docs) applied to .lore.md known-rule text, e.g. grep the uv --frozen rule after each re-distillation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

Interim guard shipped (PR #145, squash-merged 2026-11-08):
`tests/docs/test_lore_md_rules_survive.py` fails the suite when a load-bearing
rule's anchor vanishes from `.lore.md`. Three rules pinned — uv --frozen
("re-locks uv.lock"), requires_map undefined skips removal ("skip the removal
rather than assume it is harmless"), work repos never enter the committed
catalogue. Anchors are body phrases, not titles, so a title/body swap that
keeps the body still passes (survival is the bar, not placement). The codex
decision-pointer defect is deliberately not canaried — it is still broken, so
a guard on it would be permanently red.

Remaining scope (not addressed here): the upstream report to BYK/loreai
(DOT-298 pattern), and reconciling the codex wrong pointer. The pointer is
wrong in the *body*, not the title: the entry title says "(decision-4)" and
decision-4's own title is "codex routes through the Lore gateway; DOT-104's
premise is retired", but the body cites "decision-2". `.lore.md` is
captures-only, so the fix is a lore re-capture, not a hand-edit.

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

The interim guard is in place and merged. This task's headline defect — silent
loss of load-bearing rules during re-distillation — is now caught in the suite
instead of in review. The two remaining items (upstream report, codex pointer)
are deliberately deferred and recorded above.

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-beacdac9fe164fac8aeb824b3e3faeba
type: claim_task
actor: opencode-session
timestamp: '2026-11-08T21:34:58.031333Z'
result: succeeded
task_id: DOT-305
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Interim .lore.md drift-guard test (tests/docs pattern); worktree .worktrees/dot-305 on agent/dot-305
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-fdd7d4983b124f99bd77914faa280450
type: release_task
actor: opencode-session
timestamp: '2026-11-09T00:04:32.004254Z'
result: succeeded
task_id: DOT-305
from_status: inprogress
to_status: todo
```
Interim drift guard merged (PR #145); retro follow-ups merged (PR #147); remaining scope recorded in task
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->

## State as of 2026-11-10 — read before starting

**`main` is red, and the cause is this task's subject.** One test fails on a
clean `origin/main` (`39e6acaca`):

```
tests/docs/test_lore_md_rules_survive.py::test_rule_survives_redistillation[requires_map undefined skips removal]
1 failed, 4 passed
```

**What happened.** Commit `732eaa550` ("backlog: record DOT-341 outcome and PR
#172") rewrote `.lore.md` — 68 lines changed — and silently dropped the entry
`lore:01a1bf7f-db90-77fd-8fad-43094b413e14`. That entry carried the rule
"when you are unsure whether a test-owned artifact is safe to remove, skip the
removal rather than assume it is harmless", which is exactly what
`tests/docs/test_lore_md_rules_survive.py` asserts on.

**Verified, not inferred** — the rule's presence by commit:

| Commit | Rule present |
|---|---|
| `696af7bae` | yes |
| `732eaa550` | **no** — the rewrite |
| `a9ee7892a` | no — the merge carried the loss forward |

**A fix was written and deliberately discarded.** A commit restoring the block
from `696af7bae` was prepared in a scratch worktree. The author chose to discard
it and leave the repair to this task, so nothing was pushed and `main` is
unchanged. Do not go looking for that commit; it no longer exists.

**Third sighting.** Prior occurrences are in this task's history. This one is
different in a way that matters: it was caught by the `tests/docs` guard on CI,
not by a human noticing. The guard did its job.

**The real gap.** The guard only catches a loss *after* it lands, and only for
the rules it happens to assert on. Any unguarded `.lore.md` entry can still be
dropped by a re-distillation with nothing noticing. So the durable fix is not
"restore this one block" — it is one of:

- a `.lore.md` rewrite that is structurally lossless (re-distillation that
  cannot delete an entry, only reorder or summarise it), or
- a diff check that fails a commit which removes a `<!-- lore:ID -->` block
  without an explicit deletion marker.

The second is cheaper and catches the class rather than one instance.

**Reproduction for whoever takes this:** `uv run --frozen pytest
tests/docs/test_lore_md_rules_survive.py` on a clean `origin/main`. Then
`git show 732eaa550 -- .lore.md` to see the rewrite that dropped it. Restoring
the block is a valid first move, but it leaves the class open and `main` red
again at the next rewrite.
