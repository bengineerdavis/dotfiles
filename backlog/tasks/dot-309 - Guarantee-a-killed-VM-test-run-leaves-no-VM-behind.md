---
id: DOT-309
title: Guarantee a killed VM test run leaves no VM behind
status: To Do
created_date: 2026-11-07 14:30
labels:
- bug
- testing
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Leave nothing behind when a VM test run dies. This is the leak half of
DOT-303; DOT-303 is the source-corruption half. They need separate fixes and
this task exists so neither hides the other.

Measured 2026-11-07, from the tool sources:

- Molecule 26.9.0 runs its cleanup and destroy steps ONLY inside an
  `except ScenarioFailureError` clause (command/base.py:375-384). That
  exception is raised by molecule's own steps — the verifier, idempotence, the
  worker.
- Molecule installs NO signal handlers at all: grepping its package for
  `signal.`/`SIGTERM`/`SIGINT` returns nothing. SIGKILL, SIGTERM, a CI
  cancellation, a closed laptop and a power cut all terminate the process
  without unwinding through that clause.
- `--destroy` accepts only `always|never` (default `always`) and there is no
  timeout option. A hung driver call neither fails nor finishes.

So the only teardown that exists is the one a graceful failure triggers.

**What leaks.** The repo's Lima scenario keeps the VM in
`/tmp/lima-{{ molecule_ephemeral_directory | hash('sha1') }}` — a path derived
from hashing the ephemeral directory's path. On this machine that hash of the
current location is `fc5b5f0f60b5`, and `/tmp/lima-fc5b5f0f60b59a87423c25989c8969b3a474d2fb`
was still on disk from an aborted run, holding a disk image. Nothing removed
it, and `/tmp` here is on rootfs with no age-based `systemd-tmpfiles` rule, so
it survives reboot.

`destroy.yml` is the only thing that removes it, and `cleanup.yml` removes only
`<ephemeral>/home` — never `<ephemeral>/controller`, which is where the
dangling symlink that breaks chezmoi (DOT-303) comes from.

**Migration hazard.** Because the `/tmp` name is a hash of the ephemeral dir
path, moving that directory changes the hash. A relocated configuration cannot
find VMs created under the old location: relocating to
`~/.local/state/molecule/lima/debian` hashes to `bb32d6682780`, not
`fc5b5f0f60b5`. Anything still parked under the old `/tmp` root becomes
unreachable — so DOT-303's relocation must carry a one-time sweep, and this
task's reaper must not assume every orphan is reachable by the current hash.

**The guarantee asked for.** "Whatever we do, the end result should be some
kind of condition and/or timeout that guarantees VM artifacts for test
environments are cleaned up entirely." No single mechanism delivers that; the
state model at `docs/research/topic-vm-tests/prototype-cleanup-model.html`
shows why. A timeout alone turns a hang into a failure but still leaks on
SIGKILL.

**Reviewed 2026-11-08 against what already exists — do NOT write a reaper.**
The aging mechanism is already deployed in this repo:
`home/dot_config/user-tmpfiles.d/tmp.conf` already carries
`e /tmp/opencode - - - 30d`, and `systemd-tmpfiles-clean.timer` is enabled with
a daily fire (verified active). The work is a two-line addition to existing,
scheduled, version-controlled machinery — not a new component.

The design, in four parts:

1. **Bound the run** with `timeout` in `scripts/run-molecule.sh`, so a hang
   becomes a failure with an exit code rather than a process that never ends.
2. **Age the `/tmp` remnants** by adding `e /tmp/lima-* - - - 1d` to the
   existing `tmp.conf`. Measured: the `e` type's age basis is the newest of
   access/birth/change/modify and includes ctime, so a running VM writing its
   disk stays fresh and is never reaped, while a stopped orphan ages out. Age
   1 d against a measured ~4.6 min run is a 300x margin.
3. **Make leftovers loud** at run start — a report, not a cleanup. A reaper
   that removes quietly is the current failure with a different trigger.
4. **Relocation is DOT-303's**, and is a prerequisite for a stable lease/report
   location; agree the ephemeral-dir location with that task rather than
   choosing a second one here.

Rejected after verification, so they are not re-litigated:

- **`molecule reset`** — `command/reset.py:51` is `# pragma: no cover`, and the
  driver hook (`driver/base.py:394-400`) has an empty body. Only the docker
  (`driver.py:264`) and podman (`driver.py:252`) drivers implement it, so it is
  a no-op for both drivers this repo uses.
- **`limactl prune`** — prunes unreferenced objects; an orphaned instance still
  refers to its own disk, so prune keeps it.
- **Upgrading molecule** — checked upstream `main` (newer than the current
  26.11.0): `command/base.py:377` is still `except ScenarioFailureError` and
  there is still no `signal` handling. The gap is upstream and unfixed. Worth
  reporting upstream; not a fix here.
- **A hand-rolled reaper** — duplicates a deployed mechanism and carries a
  test burden nobody budgeted for.

Known limits, stated so they are not claimed away: macOS has no systemd (the
existing `.chezmoiignore:26` conditional already excludes `tmp.conf` from
non-Linux, so points 1 and 3 apply there and the aging reaper does not); `e`
empties the directory rather than removing it; and every run currently uses the
fixed platform name `lima-mol` (molecule.yml:10, deliberate for the SSH socket
path budget), so two concurrent runs collide and a leftover cannot be
attributed to a run.

Evidence and the per-mechanism coverage table:
`docs/research/topic-vm-tests/CLEANUP-GUARANTEES.md`.

Related: DOT-303 (source corruption, the relocation half), DOT-256 (throwaway
runs must fail closed and leave no persistent state — read it first; part of
this may belong there).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A run killed with SIGKILL mid-create leaves no Lima instance, no `/tmp/lima-*` root and no disk image behind
- [ ] #2 A run that hangs indefinitely is terminated by a timeout, and its artifacts are then removed
- [ ] #3 The cleanup is proven for both an injected kill and a deliberate hang, with the mechanism named in the test
- [ ] #4 An aged-out `/tmp/lima-*` remnant is collected by the existing `systemd-tmpfiles` timer, with the rule proven against both an old and a fresh directory
- [ ] #5 An unattributable leftover makes the wrapper report it rather than continue silently
- [ ] #6 The macOS gap is stated in the owning doc rather than left implicit — the aging reaper is Linux-only
- [ ] #6 `scripts/run-molecule.sh` still passes its existing contract tests, and `bash -n` is clean
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Read before starting: DOT-256 (throwaway-session cleanup rules) and DOT-303
(relocation). DOT-303's relocation is a prerequisite for a stable lease
location — agree the ephemeral-dir location with that task rather than
choosing a second one here.

Observations recorded while filing, so they are not re-derived:

- `limactl delete` (2.2.1) takes only `-f/--force`; there is no TTL and no
  auto-reap. The instance registry is `~/.lima`, which here holds only
  `_config` because the wrapper relocates `LIMA_HOME` to `/tmp`.
- `vagrant global-status --prune` (2.4.9) clears stale RECORDS; it does not
  destroy a running domain. `virsh list --all` is empty on this host today.
- Do not delete the orphan currently on disk without asking — it is VM state.
  `/tmp/lima-fc5b5f0f60b59a87423c25989c8969b3a474d2fb`, ~90 MB.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Killing a VM test run in the middle provably leaves no artifact, and recovering needs no manual step beyond re-running the wrapper
<!-- DOD:END -->