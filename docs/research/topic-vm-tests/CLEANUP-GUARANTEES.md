# VM cleanup guarantees for topic Molecule runs

What actually gets cleaned up, what does not, and what a guarantee would require.

Measured 2026-11-07 on pop-os. Versions: molecule 26.9.0, limactl 2.2.1, Vagrant 2.4.9, ansible-core via the pinned `test-vm` group. Every claim is tied to a source in § Sources.

## Conclusion

- **Nothing guarantees cleanup.** Molecule runs its cleanup and destroy steps only when its own scenario loop raises `ScenarioFailureError`. A run killed by SIGKILL, a CI cancellation, a closed laptop, or a timeout does not raise it, and molecule 26.9.0 installs **no signal handlers at all** — so nothing runs.
- **The ephemeral directory is bookkeeping, not the VM.** Deleting it does not delete the VM. On this repo's Lima scenario the real VM state lives at `/tmp/lima-<sha1>`, derived by hashing the ephemeral directory's path. Delete the ephemeral dir and you orphan a VM and its disk.
- **`/tmp` does not save you.** On this machine `/tmp` is on rootfs, not tmpfs, and no age-based `systemd-tmpfiles` rule clears it. An orphaned `/tmp/lima-*` survives reboot indefinitely. A live orphan proved it: ~90 MB from a killed run was still present two days later.
- **Relocation is necessary but not sufficient.** Moving the ephemeral dir out of the chezmoi source fixes the source-corruption class (DOT-303) and does nothing for a leaked VM. A guarantee needs both.
- **The two failure classes are separate.** DOT-303 as filed conflated them: (a) the source tree breaks when a killed run leaves a dangling symlink in it; (b) the VM and disk leak when teardown does not run. (a) needs relocation; (b) needs a reaper and a timeout.

## What the ephemeral directory is (and is not)

`MOLECULE_EPHEMERAL_DIRECTORY` (env) maps to `scenario.ephemeral_directory` (molecule/config.py:381). It holds molecule's bookkeeping:

| Entry | What it is | Size |
|---|---|---|
| `state.yml` | created / converged / driver flags | bytes |
| `inventory/`, `ansible.cfg` | generated provisioner config | KB |
| `instance_config.yml` | host/user/port/identity per platform | bytes |
| `<platform>.yaml` | rendered driver config (`lima-mol.yaml` here) | KB |

Because the wrapper pins it into the scenario directory, this repo also puts two large things there:

- `controller/.local` — the entire checksum-verified `limactl` install for the run
- `home/` — the disposable HOME the topic installs into

**It does not hold the VM.** `lima_home` is `/tmp/lima-{{ molecule_ephemeral_directory | hash('sha1') }}` (shared/create.yml:11). The instance, its qcow2 disk, and its SSH key live there.

### Deleting the ephemeral directory orphans the VM

The `/tmp` path is a **hash of the ephemeral directory path**, so it is only derivable while that path is known:

```
sha1('/home/bdavis/.local/share/chezmoi/home/dotfiles/apps/lima/molecule/debian/.molecule')
  = fc5b5f0f60b59a87423c25989c8969b3a474d2fb
```

That is a real directory on this machine — the orphan from an aborted run, still holding a disk image. It matches exactly.

Two consequences:

1. **Delete the ephemeral dir and the `/tmp` root becomes unreachable.** `destroy.yml` recomputes the hash from `molecule_ephemeral_directory`; with the dir gone the recomputation fails and the VM is orphaned permanently — nothing names it any more.
2. **Relocating the ephemeral dir changes the hash.** Moving it to e.g. `~/.local/state/molecule/lima/debian` yields `bb32d6682780`, so the moved configuration can no longer find VMs created under the old location. Relocation must be paired with a one-time sweep, not just a variable change.

## Lifecycle and crash behaviour

`molecule test` runs: `dependency, cleanup, destroy, syntax, create, prepare, converge, idempotence, side_effect, verify, cleanup, destroy` (constants.py:127-140). The trailing `destroy` is the normal-path cleanup.

`--destroy` accepts only `always|never`, defaulting to `always` (verified from `molecule test --help`). No third option, no timeout option.

The guarantee mechanism is one `except` clause (command/base.py:375-384):

```python
try:
    execute_scenario(scenario, shared_state=scenarios.shared_state)
    scenarios.results.append(scenario.results)
except ScenarioFailureError:
    if command_args.get("destroy") == "always":
        _handle_scenario_failure(...)
    raise
```

`_handle_scenario_failure` runs `cleanup`, then `destroy`, then `scenario.prune()` (command/base.py:281-317). So teardown is reliable **only for exceptions molecule itself raises** — `ScenarioFailureError` from the verifier, idempotence, or the worker (exceptions.py:44).

It does not cover:

- **SIGKILL** — no handler possible.
- **SIGTERM / SIGINT** — no handler installed (grepped molecule for `signal.`/`SIGTERM`: zero hits), so Python's default terminates without unwinding.
- **CI cancellation** — arrives as SIGTERM, then SIGKILL.
- **Power loss / reboot.**
- **A hung driver call** — no timeout, so the run neither fails nor finishes.

Idempotency: each subcommand is individually re-runnable, so re-running `destroy` after a crash is safe. `create` is not idempotent against a *running* instance of the same name — it fails rather than adopting it.

## Where artifacts accumulate

| Artifact | Location | Large? | Cleared by |
|---|---|---|---|
| Lima instance + disk | `/tmp/lima-<sha1>` | **yes** — ~90 MB observed | `destroy.yml` only |
| Lima instance registry | `~/.lima` | small | `limactl delete` |
| Molecule bookkeeping | scenario `.molecule/` | small | `molecule reset` / cleanup |
| limactl install | `<ephemeral>/controller/.local` | **yes, hundreds of MB** | nothing |
| Disposable home | `<ephemeral>/home` | medium | `cleanup.yml` |
| Vagrant box cache | `~/.vagrant.d` | **yes** (shared by design) | never — intentional |
| libvirt domains/volumes | libvirt pool | **yes** | `vagrant destroy` / `virsh` |
| SSH key dir | `/tmp/lima-<sha1>/_config` | small | with the `/tmp` root |
| Rendered configs | `<ephemeral>/*.yaml` | trivial | cleanup/destroy |

`cleanup.yml` removes only `<ephemeral>/home`. `destroy.yml` removes `/tmp/lima-<sha1>`. **Nothing removes `<ephemeral>/controller`** — where the dangling `share/doc/lima/templates` symlink lives that breaks chezmoi.

Vagrant path: domains live in libvirt; `vagrant global-status --prune` clears stale *records* but does not destroy a running domain. `virsh list --all` is empty on this host today.

## Available timeout / TTL / lease mechanisms

- **Molecule:** no `--timeout`, no lease, no TTL. `molecule reset` looks like a
  candidate but is not one: `command/reset.py:51` is `# pragma: no cover`, and the
  driver hook it relies on (`driver/base.py:394-400`) has an empty body. Only the
  docker (`driver.py:264`) and podman (`driver.py:252`) drivers implement it, so it
  is a no-op for both drivers this repo uses.
- **Lima:** no auto-reap. `limactl delete --force` is manual. `limactl prune` prunes
  *unreferenced objects* only — an orphaned instance still refers to its own disk, so
  prune keeps it. Useful for cache size, not for orphans.
- **Vagrant:** none. `global-status --prune` is record hygiene, not reaping.
- **Upgrading molecule does not help.** Checked upstream `main` (newer than the
  current 26.11.0 release): `command/base.py:377` is still `except
  ScenarioFailureError`, and there is still no `signal` import or handler anywhere in
  it. The gap is upstream and unfixed.
- **`/usr/lib/tmpfiles.d/tmp.conf:11`** is `D /tmp 1777 root root -` — a *create*
  rule, not an age rule, and `/tmp` is on rootfs (not the tmpfs that would clear on
  reboot). So the distro does not reap it.

### But the aging mechanism already exists and is deployed here

`systemd-tmpfiles` supports age-based cleanup with the `e` type plus an age argument,
and **this repo already uses it**: `home/dot_config/user-tmpfiles.d/tmp.conf` carries
`e /tmp/opencode - - - 30d`, and `systemd-tmpfiles-clean.timer` is enabled with a
daily fire (verified active: next fire scheduled, last fire 21 h ago). That file is
already excluded from non-Linux targets by `.chezmoiignore:26`.

Measured behaviour, with an isolated `XDG_CONFIG_HOME` and a glob rule:

```
Running clean action for entry e /…/.scratch/tf3/lima-*
Cleanup threshold for directory "/…/lima-old" is Sat 2026-11-07 14:45:01.199149 PST
  age-by: abcmABM
```

Two properties, both measured rather than assumed:

1. **The age basis is the newest of access/birth/change/modify — and it includes
   ctime.** `touch -d` cannot forge ctime, so the check cannot be gamed by a process
   touching its own files. A file aged to 5 days with `touch -d` was still rejected:
   "change time … is too new".
2. **That fits this case closely.** A *running* VM writes its disk continuously, so
   its timestamps stay fresh and it is not reaped. A *stopped* orphan accumulates age
   and is collected.

Glob support is real: a `lima-*` rule matched two directories and evaluated each one
separately. `e` cleans a directory's *contents*; it neither creates nor removes the
directory, so a live run's root is untouched.

### And a watchdog is available

`systemd-run --on-active` works for transient timers — verified live (unit created,
`EXIT=0`, next fire scheduled). `timeout` is present at `/usr/bin/timeout`.

So the only cleanup that exists *by default* is the one the `except` clause triggers.
The machinery to bound and age it is already installed.

## What a guarantee would have to look like

No single mechanism closes every failure mode. Each candidate, with its blind spot:

**M1 — destroy-on-failure (current).** Covers `ScenarioFailureError`. Misses kill, cancel, reboot, hang.

**M2 — relocation out of the chezmoi source.** Covers the source-corruption class outright. Does nothing for a leaked VM.

**M3 — run timeout.** A wall-clock bound in the wrapper turns a hang into a failure with an exit code. Misses SIGKILL (the process is already gone).

**M4 — lease + reaper.** Write a lease (run id, pid, created-at) at start, delete it on successful teardown, and sweep expired leases at wrapper start. Covers every failure mode that leaves state behind, because the *next* run cleans up the previous one. Misses: a machine that never runs a test again never reaps.

### The decision: use the existing mechanism, do not write a reaper

Reviewed against what already exists (see § Available timeout / TTL / lease
mechanisms). The aging half is **already deployed in this repo** — a two-line
addition to machinery that is installed, scheduled, and version-controlled beats a
bespoke reaper that duplicates it and rots when `tmpfiles` semantics change.

1. **Relocate** the ephemeral dir outside `home/` (fixes DOT-303's class), with a
   one-time sweep of old `/tmp/lima-<oldhash>` paths.
2. **Bound the run** with `timeout` in `scripts/run-molecule.sh`, so a hang becomes a
   failure with an exit code rather than a process that never ends.
3. **Age the `/tmp` remnants** by adding `e /tmp/lima-* - - - 1d` to the existing
   `home/dot_config/user-tmpfiles.d/tmp.conf`. Age 1 d against a measured ~4.6 min run
   is a 300× margin, so a live run cannot be reaped, while a stopped orphan ages out.
4. **Make leftovers loud** at run start. A reaper that removes quietly is the current
   failure with a different trigger. This is the only part needing new code, and it is
   a report, not a cleanup.

Rejected, with reasons:

- **A hand-rolled reaper script** — duplicates a deployed mechanism, adds its own test
  burden, and is a bespoke solution to a solved problem.
- **`molecule reset`** — a no-op for both drivers this repo uses (see above).
- **`limactl prune`** — an orphan still refers to its own disk, so prune keeps it.
- **Upgrading molecule** — upstream `main` carries the same gap.
- **`systemd-tmpfiles` type `d` or `q`** — `e` is correct because it cleans contents
  without creating or removing the directory.
- **Age `0`** — unconditional delete on every clean run would reap a live VM.

M1 stays as the fast path; it is just not the guarantee.

### Limits of this answer, stated

- **macOS has no systemd.** `tmp.conf` is excluded from non-Linux targets by the
  existing `.chezmoiignore:26` conditional. Points 2 and 4 still apply on Darwin; the
  aging reaper does not. Do not claim cross-platform coverage.
- **`e` empties the directory, it does not remove it.** An emptied `/tmp/lima-<sha1>`
  remains. Harmless, but say so rather than implying full removal.
- **A live but idle VM older than the threshold would be reaped mid-run.** At 1 d
  against runs of minutes this is unreachable today; point 2 keeps it that way.
- **Nothing here reaps a VM whose `/tmp` root is unreachable** because the ephemeral
  directory moved. That needs the one-time sweep in point 1.
- **Every run uses the same platform name.** `home/dotfiles/apps/lima/molecule/debian/molecule.yml:10`
  fixes it at `lima-mol` (deliberately — the SSH socket path must stay under
  `UNIX_PATH_MAX=104`), so two concurrent runs collide and a leftover cannot be
  attributed to a run. Point 4 can only report what it can name.

## Sources

- `molecule/command/base.py:281-317` — `_handle_scenario_failure` (cleanup, destroy, prune)
- `molecule/command/base.py:370-384` — the `except ScenarioFailureError` gate and `--destroy always` check
- `molecule/constants.py:112-140` — `test_sequence`, `destroy_sequence`, `create_sequence`
- `molecule/config.py:381` — `MOLECULE_EPHEMERAL_DIRECTORY` → `scenario.ephemeral_directory`
- `molecule/exceptions.py:44` — `ScenarioFailureError`
- `molecule/verifier/testinfra.py:198`, `molecule/worker.py:236`, `molecule/command/idempotence.py:58,67` — the only raisers
- `uv run --frozen --group test-vm python -m molecule test --help` — `--destroy [always|never]`, default `always`; no timeout flag
- `grep -rn "SIGTERM|SIGINT|signal\." molecule/` — zero hits (no signal handling)
- `limactl delete --help` (2.2.1) — `-f/--force` only, no TTL
- `vagrant global-status --help` (2.4.9) — `--prune` is record hygiene
- `virsh list --all` — empty, no stray domains
- `/usr/lib/tmpfiles.d/tmp.conf:11` — `D /tmp 1777 root root -` (create, not age)
- `mount | grep " /tmp "` — no separate mount; `/tmp` is on rootfs
- `sha1('<…>/.molecule')` = `fc5b5f0f60b59a87423c25989c8969b3a474d2fb` — matches the observed orphan directory
- `home/dotfiles/apps/lima/molecule/shared/create.yml:11` — `lima_home` hash derivation
- `home/dotfiles/apps/lima/molecule/shared/destroy.yml` — stop/delete `/tmp/lima-<sha1>`
- `home/dotfiles/apps/lima/molecule/shared/cleanup.yml` — removes `<ephemeral>/home` only
- `scripts/run-molecule.sh:105` — the `MOLECULE_EPHEMERAL_DIRECTORY` pin inside the source
- `docs/research/topic-vm-tests/PLAN.md` § Destroy safety, § Decision 4 — repo's own ruling, measured ~4.6 min/run
