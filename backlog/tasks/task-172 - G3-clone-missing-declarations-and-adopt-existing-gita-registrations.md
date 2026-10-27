---
id: TASK-172
title: G3 — clone missing declarations and adopt existing gita registrations
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:gita-and-machine-file-backup-approved-2026-09-23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**G3 — clone missing declarations and adopt existing gita registrations.**
  After the BK2–BK4 real-data gate, scaffold standalone `dotfiles/apps/gita`
  with `topic_provides: [gita]` and `topic_requires: [mise, python, git]`.
  Mise provides Python; git comes from apt/Homebrew prerequisites and is
  probed on PATH as in `apps/chrome`. Do not wait for the queued `apps/git`:
  it owns git configuration, not the binary. Claim
  `dotfiles/apps/mise/files/config.toml` before taking ownership of its
  existing `pipx:gita` entry using first-party mise commands, the herdr pattern.
  Resolve the repo list in `dotfiles/roles/repo-context`, modelled on
  `roles/topic-resolution`. Gita initially reads it role-relatively, like
  `config/editors.yaml`; the queued `topic_subscribes` machinery later makes
  the behaviour-preserving switch, as already planned for vscode.
  Match existing clones by normalised host/owner/repo remote before cloning
  anything. Keep the normaliser pure and property-tested. Report matches
  outside the declared layout type; never relocate them automatically.
  Groups mirror layout types, one per type. Registration recurses, excludes
  `.venv`, and detects duplicate-basename collisions; membership cites paths
  under the type directory, never bare names. `gita ls` is one line, so any
  local count uses `wc -w`, not `wc -l`; keep measured counts out of the queue.
  Adopt each target's existing `~/.config/gita/repos.csv` baseline instead
  of rediscovering it, checking existence and provenance on that target.
  The earlier study attributes its baseline to the Mac on 2026-09-15; the
  later handoff says "this box" but identifies its session as Linux. Do not
  assume that the Mac's observed baseline exists on Linux.
  Never auto-trust SSH host keys. Bootstrap already clones via SSH to
  github.com on a provisioned machine; report another untrusted host once.
  Tag clone-new tasks `[install, upgrade]`, since `update.sh` requests only
  `upgrade`. With no local pick, report and do nothing. Removal unregisters
  gita entries and drops the topic's mise entry, never clones. During normal
  reconciliation, unregister entries removed from declarations only with
  `gita_unregister_removed`, default off.
  Done when both-OS templates render with `StrictUndefined`, deliberate
  breaks fail the tests with mutation trailers, and `--check` on the Linux
  target changes nothing. This hands clone/registration state to G4.
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
