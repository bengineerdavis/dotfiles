---
id: DOT-171
title: G2 — document and establish the catalogue and machine-file contract
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:gita-and-machine-file-backup-approved-2026-09-23
updated_date: 2026-11-04 20:50
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**G2 — document and establish the catalogue and machine-file contract.**
  After G1, BK1 and the second-machine inventory, add
  `dotfiles/config/repos.yaml`: personal repos and remotes, one shared set
  initially, with personal discovery sources. Remotes have their own file;
  adding or removing a declaration means editing that file and running the
  topic. This is a distinct catalogue domain with a subscriber and domain
  truth, not data to fold into `editors.yaml` or `agents.yaml`.
  Machine identity is named sets plus an unversioned local pick under
  `~/.local/state/machine/`, never a committed hostname. Split local files by
  what may travel: `machine.yaml` holds set picks, discovery modes and
  schedule; `private.yaml` holds personal private entries; `work.yaml` holds
  work entries and sources. Machine-written sync/discovery records live
  separately from hand-edited files, preserving comments, and are rebuilt
  rather than backed up. Declarations say what should exist; gita and disk
  say what is actually cloned or registered. A machine with no local pick
  gets a report and nothing else.
  Migrate `dotfiles/machines.yml` away from hostnames and update
  `docs/LAYOUT.md` to describe named sets and local selection. Live machine
  files are retained until the machine is decommissioned. Apply the approved
  agent-read denial for `~/.local/state/machine/`, following the
  `~/.local/state/chezmoi/` precedent in `dotfiles/docs/MULTI-MACHINE.md`;
  this permissions change needs policy-path PR review. No real machine-file
  seeding before BK2–BK4 prove backup and recovery.
  Done when the format and a working example are documented, the files
  parse, and no machine hostname values remain in the current tree. This
  hands the file contract to BK2 and, after the real-data gate, G3.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-11-04 (TASK-242): two parts of this contract already landed, so the
remaining scope is narrower than the description above reads.
- `dotfiles/machines.yml` no longer carries hostnames: its per-machine
  `repos:` block (keyed by a hardware serial, no consumer) is deleted, and the
  six Mac-only entries it held were migrated into `config/repos.yaml`. The file
  is now solely the provisioning-answers registry, keyed by `ansible_hostname`
  only where the hostname passes spec.md § Data's string test.
- The "never a committed hostname" goal is therefore met for machines.yml, but
  NOT repo-wide: `.chezmoidata/uv.yaml` and `.chezmoidata/opencode.yaml` still
  key by `chezmoi.hostname` (both entries are no-ops today — empty map and
  `work: false` — so the remaining work is deciding the key scheme for those
  two files, not fixing behaviour).
- Still open here, unchanged: the named-set model, the unversioned local pick
  under `~/.local/state/machine/` (`machine.yaml` / `private.yaml` /
  `work.yaml`), the agent-read denial for that path (policy PR), and the
  BK2–BK4 real-data gate before seeding.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
