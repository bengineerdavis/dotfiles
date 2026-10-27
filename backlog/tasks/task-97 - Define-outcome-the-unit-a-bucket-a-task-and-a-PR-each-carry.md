---
id: TASK-97
title: Define "outcome" — the unit a bucket, a task and a PR each carry
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Define "outcome" — the unit a bucket, a task and a PR each carry.**
  [question for the author, 2026-09-24 — no session holds it] Ask: adopt the
  definition drafted since in another of the author's repositories (local,
  unpublished; it grew out of the council below), and if so, share it or
  keep a local copy here? That draft settles "outcome" as the part of the
  work a reviewer accepts or rejects for one reason, with everything needed
  to judge it (split rule, join rule, the "and" sentence as a smell), and
  adds riders, merge-gate classes and a task/change nesting. Review it
  against the verdicts below before recording anything.
  `docs/WORKTREES.md` § Bucketing says a bucket is one outcome, tested by a one-sentence
  description without "and", but never says what an outcome is. Gather the
  leading candidates, put them to an advisor council (sub-items below), and
  bring a recommendation to the author, who has a candidate of their own.
  Done when the author has chosen a definition and it is recorded — in
  `docs/GLOSSARY.md` and § Bucketing — with the council's dissent kept beside
  it. Branch and worktree `outcome_definition`, stacked on `docs_bucketing`.
  - **O1 — domain-modelling advisor.** [agent: general/outcome-o1] Judge the
    candidates through bounded contexts and aggregates, mapped onto this
    repo's topics and roles. Research only; done when a written verdict names
    a preferred definition, its failure cases, and what it rejects.
  - **O2 — revert-and-history advisor.** [agent: general/outcome-o2] Judge
    the candidates by what history needs: revert, bisect, cherry-pick,
    changelog. Research only; same done-condition as O1.
  - **O3 — reviewer advisor.** [agent: general/outcome-o3] Judge the
    candidates by what a reviewer who was not in the session can hold and
    decide on. Research only; same done-condition as O1.
  - **O4 — agent-operability advisor.** [agent: general/outcome-o4] Judge
    whether an agent can apply each candidate consistently, and what a
    mechanical check (a future determinant function) could and could not
    decide. Research only; same done-condition as O1.
  - **O5 — skeptic.** [agent: general/outcome-o5] Argue against every
    candidate: solo-developer cost, messy existing history, the transition
    period, where each definition over- or under-splits. Research only; same
    done-condition as O1.

  **Council verdicts, 2026-09-24** (five `general` subagents, one model, five
  lenses — not a mixed-model council):
  - *Agreed by all five:* tests, TASKS.md lines, handoff pointers, changelog
    fragments and review fixups ride with their outcome and never count as
    one. #11 is one outcome, since a role with no caller cannot be judged, so
    it joins its first caller. #8 was three or four outcomes. #10 is one.
    Rejected: entity+verb alone (the component cut AGENTS.md forbids; #8 passes
    it with several decisions in one file); owner-facing capability (excludes
    refactors, docs, governance); done-condition alone (circular).
  - *Mostly agreed:* #9 is one (O4: two). #12 is two, kept together by the
    author's choice (O1, O3, O4, O5). "One sentence without 'and'" is gameable
    by abstraction ("tighten git permissions" hides #8), so it is a smell, not
    a gate: write it at the level where a rejection would be stated.
  - *Against the coordinator's composite:* "one owner" rejects #11 and renames
    (O2, O5). "One check can prove" invites ceremony tests for docs, which is
    Class B evidence (O3, O4, O5); if kept, the check must be named before the
    work (O4). Revert independence only needs to hold one way (O2).
  - *O1 domain:* owner = whoever must undo it (a topic's remove.yaml); proof
    sits inside that boundary. Define the nesting: a commit is one decision,
    an outcome is one or more decisions, a task delivers one outcome.
  - *O2 history:* merge commits make the PR the outcome at `--first-parent`
    level and the commit the decision; cherry-picked buckets lose original
    SHAs, so one changelog fragment per bucket becomes the history record.
  - *O3 reviewer:* split by reasons to reject; join by evidence needed to
    judge. The quiz before merge should need one question.
  - *O4 agent operability:* mechanical census of owners and merge-gate classes
    surfaces "probably several outcomes", never blocks; bucketing by gate
    class first keeps self-mergeable parts self-mergeable and is the only
    split that comes out the same every session.
  - *O5 skeptic:* do not define tightly; the cost of splitting lands on the
    one human reviewer, so split hardest where a wrong merge cannot be undone
    (policy, deployed files) and loosest where it can (docs, TASKS.md); apply
    to new buckets only, never rewrite merged history.
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
