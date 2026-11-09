---
id: DOT-334
title: Investigate why the research subagent reports success without writing its file
status: To Do
created_date: 2026-11-09 01:30
labels:
- tooling
- agents
- research
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The `research` skill dispatches a background subagent to investigate a question
against primary sources and write one Markdown file. On this machine the
subagent has returned a session summary — a normal, successful-looking
completion — **six times**, and written no file.

Each occurrence looked identical: the dispatch returned a paragraph of prose
describing what the agent had been doing, with no error, no non-zero status,
and no artefact. Twice the return text was a plausible-looking summary of the
work, which is worse than a failure, because it reads like success.

The work still got done — the parent agent noticed the file was absent, listed
for it, found nothing, and did the research inline. That is a correct recovery
and a bad steady state: it silently converts a parallel background task into
serial foreground work, and a less careful parent would report the summary as
if the research had happened.

Six occurrences in one session is a pattern, not flakiness.

## What to investigate

This is an investigation task: the output is a diagnosis and a decision, not
an implementation.

1. **Does the subagent believe it wrote the file?** Capture its own account of
   what it did, rather than inferring from the absence. The distinguishing
   question is whether the write was attempted and failed, attempted against a
   path that does not exist, or never attempted at all.
2. **Is the path the problem?** Both failures observed this session targeted
   files under a directory that did not exist yet in the checked-out tree
   (`copier-template-copier-template/docs/research/` existed locally but not on
   the branch the subagent was given). A write into a non-existent directory
   fails in a way a summarising agent may not surface.
3. **Is the working directory the problem?** The subagent inherits a cwd that
   may be a worktree, a main checkout held by another session, or a stale path
   after a worktree was removed. Verify which, in the failing case.
4. **Does the tool report partial completion as success?** Determine what the
   subagent's final message is composed of and whether an interrupted or
   tool-failed run still yields a summary.

## Proposed shape, to validate rather than assume

Make "completed but wrote nothing" structurally impossible rather than
detectable: have the subagent write a **stub file first** (heading plus the
question), then fill it. A stub is cheap, it fails loudly at the point where a
missing directory or a bad path is discovered, and it leaves evidence the
parent can check before trusting the summary.

If the investigation shows the write is being attempted and failing, this
degrades to a better error message — still worth it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
1. A reproduction exists: the conditions under which the subagent returns a
   summary without a file are stated precisely enough for a second session to
   trigger them.
2. The cause is identified from evidence (the subagent's own tool results, or
   a re-run with logging), not inferred from the absence of the file.
3. A fix or mitigation is chosen and recorded, with the rejected alternatives
   and why — including the stub-first shape if it is not chosen.
4. If the cause is a directory or path issue, the fix is verified against that
   exact case, not only against a path that already exists.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Raised 2026-11-09 from the retro on the session that built the worktree guard
and the branch-ownership module.

Occurrences observed in that session, both against
`/home/bdavis/code/projects/personal/templates/copier-template-copier-template/docs/research/`:

- `repo-types.md` — dispatched to research the generic repository-type
  taxonomy. Returned a summary, wrote nothing, research done inline.
- `worktrunk-guard.md` — dispatched to check the guard against Worktrunk's
  documentation. Same outcome.

Both dispatches named an absolute destination path that did not exist on the
branch under investigation. That is the leading hypothesis and it is unproven —
which is precisely why this is an investigation task rather than a fix task.

Recovery pattern that worked, for the record: after any research dispatch,
**check for the artefact before reading the summary** (`ls` the target, or
`find` for the filename). A summary is not evidence of a file.

Both eventual files did land, written inline by the parent instead — so each
is a reproduction case for what a successful write looks like from the other
side of the failure:

- copier-template-copier-template
  [#1](https://github.com/bengineerdavis/copier-template-copier-template/pull/1)
  (`84be534`) — `docs/research/repo-types.md`.
- The same PR — `docs/research/worktrunk-guard.md`.

Worth noting for the investigation: the directory `docs/research/` did not
exist on `origin/main` when both dispatches ran. It exists now. If the cause
was a missing parent directory, a re-run against the current tree would pass
and tell you nothing — reproduce against a branch that still lacks it.

The skill itself is unmanaged (`~/.config/opencode/skills/research/`, not
deployed by chezmoi), so the fix lands there or in the agent runtime, not in
this repo. This task owns the diagnosis and the decision; it does not own the
implementation site.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
1. The cause is stated with evidence and a mitigation is either landed or
   handed to the owning repo with the diagnosis attached.
<!-- DOD:END -->
