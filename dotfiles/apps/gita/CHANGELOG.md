# gita — changelog

Section names come from antsibull-changelog; see `docs/TOPICS.md`
§ "Per-topic changelog and local edge cases".

## 2026-10-18

### release_summary

Topic created as the gita stopgap. It registers the repos on disk from the
committed catalogue and gives a `--tags upgrade` sync path, so repos sync
most of the time while `redge-cli` is built.

### minor_changes

- Add `topic.yml` (`topic_provides: [gita]`, `topic_requires: [mise, git]`):
  mise installs the binary, this topic owns the `pipx:gita` entry via
  first-party mise commands (herdr pattern).
- `install.yaml` claims the entry (`mise use -g pipx:gita`, probe-first),
  probes `gita`, loads `config/repos.yaml`, and registers each cloned repo
  with `gita add <path> -g <group>`; declared-but-uncloned repos are skipped
  and reported.
- `upgrade.yaml` adds the sync path: `gita fetch` then `gita pull`, both
  non-failing so a bad repo reports rather than aborts the run.
- `remove.yaml` unuses the `pipx:gita` entry (`mise unuse --global`, probe-
  first) and clears the registration behind `gita_remove_registration`
  (default off); never deletes clones.
- Seed `dotfiles/config/repos.yaml` with the ownership split of the repos on
  the Linux box (personal / forks; work empty).

### known_issues

- **Paths are unmigrated.** The catalogue points at the current
  `projects/…` locations, not the `docs/LAYOUT.md` type dirs; the phase-4
  migration re-points these and gita re-registers on move.
- **Duplicate basenames collide in gita.** gita names a repo by its basename,
  so two repos with the same name (e.g. two `gitignore` clones) cannot both
  register; the catalogue carries only one.
- **`work/` untested.** The work group has no members on the author's own
  machines and has not been exercised on the work Mac.
- **Unverified gita behaviours.** gita 0.16.8.2's exact exit codes for
  fetch/pull on a no-remote repo were not measured; the tasks treat any
  non-zero as "report, don't abort" rather than parsing the output.