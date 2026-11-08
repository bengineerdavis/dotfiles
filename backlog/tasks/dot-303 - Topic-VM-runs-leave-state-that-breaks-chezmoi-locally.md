---
id: DOT-303
title: Topic VM runs leave state that breaks chezmoi locally
status: To Do
created_date: 2026-11-07 12:20
labels:
- bug
- testing
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Check for existing work before starting.** This overlaps DOT-256 (throwaway
runs must fail closed and leave no persistent state) and DOT-255 (the Molecule
VM matrix). Read both first: this may be an acceptance criterion on one of them
rather than a separate piece of work. It is filed because the failure is live
and specific, and because a merge-gate run on this host cannot currently come
out green.

A Molecule run that never created a VM leaves a partial
`.molecule/controller/` tree under the chezmoi source, containing a broken
symlink. `chezmoi` walks the source and dies on it, which fails unrelated
tests:

```
tests/chezmoi/test_config_identity.py::test_config_template_keeps_its_data_section  FAILED
tests/chezmoi/test_gitconfig_tools.py::test_mergetool_labels_all_three_panes        ERROR
tests/chezmoi/test_gitconfig_tools.py::test_difftool_labels_both_panes              ERROR
tests/chezmoi/test_gitconfig_tools.py::test_no_empty_named_tool_sections            ERROR
```

Measured 2026-11-07 on `main` and in a worktree, identical both places:

```
chezmoi: stat .../apps/lima/molecule/debian/.molecule/controller/.local/share/doc/lima/templates:
no such file or directory
```

What was on disk:

- `state.yml` says `created: false`, `converged: false`, `driver: null` — no VM
  was ever made.
- `inventory/ansible_inventory.yml` still names a one-shot Lima instance
  (`ansible_port: 35139`, key under `/tmp/lima-fc5b5f0f...`), and that `/tmp`
  directory is gone.
- `controller/.local/share/doc/lima/templates` is a symlink to
  `../../lima/templates`, whose target does not exist. It is the only broken
  link in the tree.

So the run created the adapter scaffolding, failed before converging, and left
both the scaffolding and a dangling link inside the chezmoi source.

**Why it stays invisible:** `.molecule/` is gitignored (`.gitignore:25`), so
it never appears in `git status`, never reaches CI, and never shows up in
review. CI is green on `main` while this host is red. Anyone whose merge gate
is a local full run hits four failures that are not theirs — exactly the
false-signal problem the known-failures table exists to remove.

Note the timestamps: the directory was created 2026-11-06 12:14 and its
`state.yml`, `ansible.cfg` and `inventory/` were rewritten 2026-11-07 09:34, so
this recurs rather than being a one-off.

Related: `docs/WORKTREES.md` and DOT-256 both hold that a throwaway run must
leave no persistent state. This is that rule failing in the chezmoi source
rather than in an agent-session directory.

Do not simply delete the directory and close this. The point is that a failed
run leaves the source tree unusable for every later run, and nothing reports
it. Deleting is the cleanup; the fix is teardown on failure.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Molecule's ephemeral directory lives OUTSIDE the chezmoi source, so no run can leave anything in it
- [ ] #2 The relocation lands with a one-time sweep of the old location — the `/tmp/lima-<sha1>` name is derived from the ephemeral dir's path, so a moved dir cannot find VMs created under the old one
- [ ] #3 A run killed mid-install leaves the source tree usable: `chezmoi apply` and `chezmoi execute-template` both succeed afterwards
- [ ] #4 The failure mode is reproducible deliberately, and the outcome is proven on both a successful run and an injected kill
- [ ] #5 Whether this is a Molecule teardown fix, a DOT-256 acceptance criterion, or both is decided and recorded on the task that owns it
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
**Revised 2026-11-07 after measurement — the original AC #4 was wrong.**

The first version of this task asked for "a check over the chezmoi source that
fails on a broken symlink". That check would pass while the bug is live:
`chezmoi managed` and `chezmoi status` stay GREEN on a dangling symlink, and
only `apply` and `execute-template` fail. Measured in an isolated scratch
source: a dot-dir holding a broken link gives managed rc=0, status rc=0, apply
rc=1, execute-template rc=1. A broken-symlink detector built on status or
managed detects nothing.

The real fix is the relocation in AC #1, plus the stale-path sweep in AC #2.

Full mechanism, from the tool sources and the repo's own playbooks:
`docs/research/topic-vm-tests/CLEANUP-GUARANTEES.md`. The state model that
shows which failure modes leak which artifacts is
`docs/research/topic-vm-tests/prototype-cleanup-model.html`.

The stale directory was present and not deleted: it is VM state, and deleting
it only clears the symptom on this host.

Scaffolding left behind at the time of filing:

```
home/dotfiles/apps/lima/molecule/debian/.molecule/
├── ansible.cfg
├── controller/.local/share/doc/lima/templates -> ../../lima/templates   (broken)
├── inventory/ansible_inventory.yml
└── state.yml   (created: false, converged: false, driver: null)
```

`limactl list` shows no instances, so nothing was running when this was
inspected.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 An aborted VM run provably leaves the chezmoi source usable, and deleting the leftover directory is no longer part of recovering from one
<!-- DOD:END -->