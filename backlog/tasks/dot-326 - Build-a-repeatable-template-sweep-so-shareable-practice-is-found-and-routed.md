---
id: DOT-326
title: Build a repeatable template-sweep so shareable practice is found and routed
  on a cadence
status: To Do
created_date: 2026-11-08 21:11
references:
- backlog/decisions/decision-5 - copier-cat-owns-refactoring-shared-lessons-from-subprojects-to-parent-templates.md
labels:
- process
- template
- copier-cat
priority: high
updated_date: 2026-11-15 21:51
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2026-11-08 three-template sweep was done by hand: read the merged PR list
and `CHANGELOG.md`, classify each shareable item against
`agentic-project-template` / `python-project-template` /
`copier-template-copier-template`, and record the routing in DOT-209. That was
one pass. The author wants a **repeatable mechanism** so the sweep is cheap to
re-run, and wants it **scheduled** so it happens without a session deciding to
do it.

The end state: a small, mechanical sweep that — on a cadence — diffs new merged
PRs / changelog entries since the last run, classifies candidate items as
shareable vs repo-specific, and emits a routing list (which template, which
entry, which PR) that a human (or a later agent) files as feature requests.

**Future home (author):** once mature, this sweep becomes something
`copier-cat` manages and installs — the sweep tool itself is a shareable piece
of template infra, so it belongs upstream in the copier-cat / meta-template
space, not baked into this repo. This DOT task is the dotfiles-side prototype
that produces the spec for that upstream piece.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
1. There is a script or doc-driven checklist that reproduces the 2026-11-08
   sweep deterministically: given a merge-base or date range, it lists the
   merged PRs and new changelog entries since that point, and classifies each
   against the three templates with the same evidence standard (primary source /
   PR number / changelog entry) used in the DOT-209 notes.
2. The sweep is scheduled — a cadence is chosen and wired the way DOT-203 is
   (a `cron:`/`schedule:` workflow, or a launchd/systemd unit per environment),
   so a run happens without a session choosing to do it. The report target is
   named, not "logs to a file nobody reads" (DOT-203 § Description has the
   anti-pattern this must avoid).
3. The sweep's own design is recorded so it can become a `copier-cat` feature:
   what it reads, how it classifies, and what its output shape is — enough for
   the meta-template repo to absorb it later. Nothing here is committed to the
   foreign copier-cat repo without its maintainer's acknowledgment
   (`AGENTS.md` § Cross-repo changes).
- [ ] #1 A task reaching Done with a template-bound note emits a routing candidate naming the target template, the source task, and the evidence
- [ ] #2 Stage one produces a draft issue or PR on the target repo, following that repo's existing branch convention
- [ ] #3 Stage two tracks the submission: maintainer feedback, HITL events, and the decision to revise or withdraw
- [ ] #4 Stage three queues migration work in this repo once the upstream change merges and releases
- [ ] #5 The ten existing upstream promises are collected as the first run: DOT-57, 208, 209, 210, 242, 307, 322, 326, 360, 361
- [ ] #6 A scheduled sweep runs as a safety net and reports candidates no event emitted
- [ ] #7 The dotfiles implementation is recorded as the prototype spec for copier-cat's planned contribute command
- [ ] #8 The stage decomposition is stress-tested against research and real submissions, and what the sketch got wrong is recorded
- [ ] #9 Architecture, spec and principles are written from what the prototype measured, not from the conversational sketch
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

**Event-driven first, sweep as the safety net (author, 2026-11-15).** The
original shape assumed a schedule. The author approved event-driven as the
primary trigger: a task reaching Done with a template-bound note emits the
candidate while the context is fresh and the evidence is still attached. The
cadence sweep stays, demoted to a safety net that catches what no event
emitted — it diffs merged PRs since the last run and reports the difference.

**The stages below are a draft to stress-test, not a conclusion.** They came
out of conversation and have no research behind them yet. Run them against
comparable projects and real submissions before treating any of it as
architecture; expect the decomposition to change. The one part carrying
evidence is that routing to a list is not a stopping point.

**Three stages, because each needs its own tasking.** Routing to a list was
the old stopping point and it is not enough; the work after routing is where
submissions stall. (1) Prepare and submit: produce the draft issue or PR on
the target repo. Whether to raise the problem or also carry the fix is a
per-item call — the ask is cheaper and the fix is more useful, and the
decision belongs with the candidate rather than set globally here. (2) Respond
upstream: track maintainer feedback and HITL events, and revise or withdraw.
(3) Migrate after merge: once the change lands and releases, queue the work to
adopt it here, plus any follow-up feedback to other repos if adoption goes
wrong. Event-driven suits all three; scheduled checks are an option for stage
two, where the waiting happens.

**Home: copier-cat is the subject-matter expert (author ruling, 2026-11-15).**
Refactoring shared lessons from subprojects up to parent templates is
copier-cat's domain, not this repo's. Verified 2026-11-15: copier-cat's README
already claims it ("push project fixes back upstream as reviewable PRs through
`contribute`"), and `copier-cat --help` lists only `merge`, `mergers` and
`adopt`, describing contribute as "phone home, planned". So the concept is
owned upstream and unbuilt. This task stays the dotfiles-side prototype that
produces the spec for it, exactly as the original note intended, and the
mechanism graduates to copier-cat rather than hardening here.

Why dotfiles prototypes it: this repo has the deepest agentic history of any
project here, so it is where the candidates and the failure modes actually
are. That is an argument for prototyping here, never for keeping it here.

Cross-references:

- **The 2026-11-08 sweep it replaces** — recorded in DOT-209 § Implementation
  Notes (the three-template classification of agentic / python / meta items).
  This task exists because that was a hand pass; DOT-326 makes it repeatable.
- **Scheduling precedent** — DOT-203 (nightly full-suite) settles the
  per-environment pattern: launchd agent on Darwin, systemd timer on Debian;
  that repo has no CI *service*, but `.github/workflows/` exists now, so a
  `cron:` workflow is also an option — settle which at implementation.
- **Sweep scope boundary** — DOT-209 already defines what is shareable vs
  excluded (anything chezmoi / Ansible / model-specific is out; agent policy,
  Python toolchain, and meta tooling are the three buckets). DOT-326 reuses that
  boundary, not re-derives it.
- **Copier-cat / meta-template** — `copier-template-copier-template` is the
  meta-template (scaffolds new templates); `copier-cat` (cc) is the template
  manager that adopts templates into projects and pushes project fixes back.
  The sweep tool is the kind of thing cc ends up installing; the meta-template
  is where a "changelog + PR classification" helper would live. DOT-315 already
  records the cross-repo filing discipline (feature request → owning repo's
  queue, maintainer acknowledgment).

Open questions to settle during implementation (not here): whether the sweep
reads only `CHANGELOG.md` (collected) or also raw `changelog.d/` fragments and
`gh pr list` (finer-grained, catches uncollected fragments); whether
classification is a deterministic keyword match (reproducible but brittle) or a
model pass (judgment track, needs the DOT-208 two-track framing); and where the
routing list lands (a backlog task like DOT-209, a `docs/research/` find, or the
upstream repo's queue directly).
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->