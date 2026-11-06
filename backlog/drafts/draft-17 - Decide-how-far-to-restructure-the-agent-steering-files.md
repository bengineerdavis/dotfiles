---
id: draft-17
title: Decide how far to restructure the agent steering files
status: Draft
created_date: 2026-11-05 04:40
labels:
- design
- process
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design draft only. The input to a `/grill-with-docs` session, not a plan.

The question: should `AGENTS.md` be restructured further, and if so along what
boundary — or is the current shape right and the remaining length acceptable?

This is deliberately a *later* decision. One slice already landed (PR #123/#124):
the trust ladder, the mutation/property/fuzzing detail, and the cross-platform
traps moved behind pointers, taking `AGENTS.md` from 1123 to 912 lines. The
question here is what, if anything, comes next, and it needs more thought than
the mechanical extraction did.

### Where the file stands now

`AGENTS.md` is ~912 lines and ~12k tokens, loaded into every session and every
subagent. It sits beside `spec.md` (599), `PRD.md` (287) and 29 files in `docs/`.

The author's constraint, stated 2026-11-04: "reducing AGENTS.md would be useful
to protect context and budget." That is the requirement this draft answers to —
not tidiness for its own sake.

### The remaining candidates, with their real cost

**1. § Commits (58 lines) duplicates `CONTRIBUTING.md`.**
The section opens by naming `CONTRIBUTING.md` as the source of truth, then
restates it "so this file is usable on its own". That is a deliberate choice, and
the question is whether it still pays. Cost of removing: an agent that never
opens `CONTRIBUTING.md` loses the granularity rule. Cost of keeping: two copies
that can drift, and about 700 tokens per session.

**2. § Working alongside other sessions (109 lines) + § Cross-session hazards.**
Heavily incident-derived: the shared-index `git commit -o` rule, the notes
refspec, the benchmark contention warning. Reference material read at the moment
of a multi-session collision, which is not every session.

**3. § Branches and integration (227 lines).**
The largest section. Contains the branching rules, the fork rule, the budget
rule, merge gates, PR descriptions, and the quiz rule. Some of this is binding
policy read constantly (merge gates); some is read once (the fork rule, the
budget rule). Splitting it by *when it is read* is the interesting cut, and it is
harder than the sections already moved because the pieces are entangled — merge
gates reference the ladder, the ladder references the gates.

**4. Cross-file duplication.**
`spec.md` and `AGENTS.md` state some of the same properties in different words.
Duplication costs maintenance and inflates a rule's apparent rank, but the spec
is normative and the guide is explanatory, so some overlap is by design. Deciding
which overlaps are load-bearing is a reading task, not a mechanical one.

**5. Move to a router.**
A short `AGENTS.md` naming a handful of always-needed rules plus a table of
"read this file when doing X", with everything else in `docs/`. This is the
logical end state of the direction already taken. Its risk is pointer-wording:
an agent that misreads a trigger never loads the rule, and the failure is silent.

### What makes this hard, and why it is a draft

Moving a section is cheap. Deciding *where the boundary is* is not:

- **Every removal is a bet on pointer-wording.** The extraction already landed
  showed this concretely: the first version of the § Conventions pointer orphaned
  five documents, and only `tests/docs/test_conventions_referenced.py` caught it.
  A rule lost that way fails silently, in the session that needed it.
- **Context load is paid once, cognitive load is paid by the human.** The
  writing-for-agents guidance is explicit that cognitive load is the price of
  human agency, spent where judgement matters. A file that is one place to look
  has value that does not show up in a token count.
- **The measurements are small.** 912 → ~700 lines saves about 3k tokens per
  session. Against a ~150k smart-zone budget that is 2%, which is real but not
  decisive. The case has to be about *clarity and drift*, not mostly about size.

### Research to do before the grill

Read first, do not guess:

- The writing-for-agents skill's information-hierarchy and pruning guidance, and
  its warning that cognitive load is not a cost to minimise.
- Which sections have been cited or followed in real sessions. `git log --grep`
  and the `.lore.md` record both hold evidence of what was actually needed.
- How other repos in this family structure their equivalent file, if any do — a
  compared example beats an argued one.
- Whether a router shape has a failure mode this repo can test for. The
  conventions test is a precedent: a guardrail made a documentation property
  mechanically checkable.

### Explicit non-goals

- Re-litigating the slice that already landed.
- Shrinking the file for its own sake. If the honest answer is "912 is fine",
  that is a valid outcome and this draft should record why.
- Changing `spec.md`, `PRD.md`, or the backlog — those are separate documents
  with their own authority.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Name the boundary a restructure would use (read-frequency, authority, or subject) and say why that boundary and not another.
- [ ] #2 For each section proposed to move or delete, state what a session loses at the moment it needs that rule, and how the loss would be caught.
- [ ] #3 Give the measured context saving and weigh it honestly against the pointer risk; a saving too small to justify the risk is a valid conclusion.
- [ ] #4 Decide the § Commits duplication specifically: which copy is authoritative, and why.
- [ ] #5 Record the rejected shapes and their reasons, so this is not re-opened blind.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Sequencing: research and grill with docs first, then the ask-matt flow
(`/grill-with-docs` → `/to-spec` → `/to-tickets` → `/implement`).

Companion evidence from the slice that landed:

- `tests/docs/test_conventions_referenced.py` requires every `docs/*.md`
  convention reachable from `AGENTS.md`. It caught five orphaned documents during
  the extraction, which is the strongest available argument that this class of
  change needs a mechanical check.
- The extraction itself: 1123 → 912 lines, three sections moved verbatim, content
  verified line for line (100 → 100, 104 → 104).

Care needed on mechanics: a commit whose `AGENTS.md` edits were unstaged while
pre-commit stashed the tree landed only the new files and left `main` red for
three tests. Stage every path explicitly before committing a move.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
