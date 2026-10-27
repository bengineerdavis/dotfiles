---
id: DOT-208
title: Build the LEDGER for the trust ladder
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build the LEDGER for the trust ladder. The ladder itself — rungs, promotion
  streaks, incident classes A-D, what is explicitly not an incident, and ageing
  — is defined in `AGENTS.md` § Trust ladder. What remains is the record. The ladder widens an agent's autonomy
  per task class and blast radius rather than globally; the ledger is what makes
  promotion evidence-based instead of felt. Rungs: 0 propose only; 1 branch and
  PR; 2 self-merge docs and tests; 3 self-merge code inside a named blast radius;
  4 unattended on a task class with an async report. `AGENTS.md` § Merge gates
  already describes rungs 2 and 3 — what is missing is the record to promote
  against. Ledger: one line per completed agent item recording the item, the rung
  it ran at, which gates passed, whether the author corrected it, and the class
  of any correction. Promote on a streak of clean items at a rung; demote one
  rung on a single incident of a defined class. The incident classes were defined before any
  promotion existed to argue about, which was the point. Note this is the same discipline `spec.md` § Evidence
  applies to measured numbers: a trust claim carries its conditions or it is an
  assertion. **[open question: whether the ledger is committed or machine-local.
  It records this repo's work rather than usage, which argues for committing it,
  but it is also a running record of agent-versus-author correction that may not
  want to be public.]**
  **Two-track model, settled with the author 2026-09-22 (shift-left study):**
  trust attaches to the *mechanism*, not the commit or session — a
  deterministic check that has proven itself doesn't re-earn trust each run.
  This is what makes trust transferable rather than reset-per-item, per the
  author: "once we've built repeatable patterns we can label as high trust,
  they should in theory be transferrable — we don't want to start from
  scratch on stages for every commit." Two tracks, not one funnel:
  - **Deterministic track** (prek/shellcheck, bats, pytest exit codes, ruff,
    ty — anything with a binary, reproducible outcome). Entry gate: seen to
    fail once (mutation-proven, per § Prove the test fails). Graduation:
    short streak of clean runs. Once graduated, trusted permanently until it
    changes or a false negative is found.
  - **Judgment track** (agent code-gen, skill output, LLM-judge verdicts —
    anything with output variance). No single-run entry gate ("passed"
    doesn't mean the same thing twice); graduates on a rolling
    correction-rate window instead of a streak, and the trust *level* moves
    with the window rather than becoming permanent.
  **Bypass state — provisional, 2026-09-22.** The ledger schema needs a
  `bypassed(reason)` state alongside ran/failed, so a `--no-verify` push is
  recorded rather than invisible. Author: "we don't yet have a more nuanced
  set of use cases and edge cases; we're still building and experimenting a
  lot, so this isn't wrong but I don't know yet" — added now as a field,
  not as settled policy on when bypassing is acceptable. Revisit once real
  bypass cases accumulate; the field just has to exist before the first one
  happens, or it gets hidden instead of recorded.
  **Auditor of the auditor — designed 2026-09-22, consolidated from the
  advisor council.** Once the ledger exists: a small trigger script (`shuf`
  over the trailing window of ledger lines — a one-liner, not a build, same
  "provisioning installs and triggers, never contains logic" shape as
  everything else here) periodically samples one past merged item and asks
  the author two questions cold, without re-reading the original quiz
  notes first: do I still understand what this changed and why, and would I
  still approve it today? Recorded alongside the ledger: item id, date,
  outcome (`still-understand` / `drifted` / `would-not-approve-now`), and
  if drifted, what didn't hold up. A drifted outcome is not an incident
  against the agent — the code didn't change — it's a signal about review
  depth at the time; two or more in a window is the trigger to look at
  whether quizzing has gotten shallow, not to relitigate the item. Cadence
  starts light (1 per ~10 merged items, or monthly, whichever is less
  frequent) and is itself a judgment-track mechanism under the two-track
  model above — it earns a tighter cadence over time rather than starting
  maximal.
  Latency tolerance is a property of *where an item sits on its track*, not a
  global clock: the funnel starts deliberately slow (least-privilege as the
  starting metaphor) and tightens toward the author's stated destination of
  under 5 seconds for fully-graduated deterministic checks, as the ladder's
  existing 5/10/20-clean-item promotion numbers are satisfied per mechanism.
  **[open question, routed rather than decided here: is a mechanism's earned
  trust keyed globally (e.g. "ruff" is trusted everywhere) or scoped per-repo
  — and is a *skill's* trust portable across repos?** This is the same
  question as the agent→function graduation policy already blocked on
  `ai-prompt-library`'s TASKS.md (§ Now, "Check AGENTS.md and CONTRIBUTING.md
  for places the agent→function graduation policy should apply") — the
  author approved routing it there rather than deciding it in this repo;
  no text lands here until that artifact exists.]
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
