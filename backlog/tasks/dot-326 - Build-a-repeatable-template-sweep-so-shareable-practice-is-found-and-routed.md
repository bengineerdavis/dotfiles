---
id: DOT-326
title: Build a repeatable template-sweep so shareable practice is found and routed on a cadence
status: To Do
created_date: 2026-11-08 21:11
labels:
- process
- template
- copier-cat
priority: medium
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
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
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