---
id: DOT-62
title: Design the cadence by which topics pull in and refresh official upstream references,
  so topics track
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Design the cadence by which topics pull in and refresh official
  upstream references, so topics track their tools proactively.** Queued
  2026-09-17 by the author: topics bind to external tools whose docs,
  changelogs and release feeds move, and today the repo learns of upstream
  change only reactively — the skillet pin needed a changelog read before
  moving, `docs/REFERENCES.md` records "when last checked" by hand, and
  cursor/vscode extension availability is being verified per editor only
  because something broke. The design must settle: what each topic declares
  about its upstream (a source list in the topic — docs URL, changelog or
  release feed, the `REFERENCES.md` row it feeds); what cadence means here
  (per-topic intervals, one repo-level sweep tied to `--tags upgrade`, or a
  machine timer — noting launchd on macOS and the systemd *user* timer rule
  on Debian); where fetched deltas land so they become work (a queue line,
  a report, a drift subcommand in the topical CLI) rather than vanishing;
  and how it composes with the extension-manifest design above, whose
  per-extension availability verdicts are the first instance of this same
  problem. **The cadence fetcher is a build** — the AGENTS.md ladder
  applies: route it (ai-prompt-library, llocallabs, or the topical CLI
  work) before any code is written here; machine-side wiring such as a
  timer is the only part that provisions. Done when a written design
  answers those questions with the destination decided through the ladder,
  and the wiring lands as queued tasks. [me]
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
