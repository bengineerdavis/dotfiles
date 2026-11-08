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

- **Molecule:** none. No `--timeout`, no lease, no TTL.
- **Lima:** none. `limactl` has no auto-reap; `limactl delete --force` is manual only.
- **Vagrant:** none. `global-status --prune` is record hygiene, not reaping.
- **The OS:** no help. `/usr/lib/tmpfiles.d/tmp.conf:11` is `D /tmp 1777 root root -` — a *create* rule, not an age rule. `/tmp` is on rootfs, so it is not the memory-backed tmpfs that would clear on reboot.

The only cleanup that exists is the one the `except` clause triggers.

## What a guarantee would have to look like

No single mechanism closes every failure mode. Each candidate, with its blind spot:

**M1 — destroy-on-failure (current).** Covers `ScenarioFailureError`. Misses kill, cancel, reboot, hang.

**M2 — relocation out of the chezmoi source.** Covers the source-corruption class outright. Does nothing for a leaked VM.

**M3 — run timeout.** A wall-clock bound in the wrapper turns a hang into a failure with an exit code. Misses SIGKILL (the process is already gone).

**M4 — lease + reaper.** Write a lease (run id, pid, created-at) at start, delete it on successful teardown, and sweep expired leases at wrapper start. Covers every failure mode that leaves state behind, because the *next* run cleans up the previous one. Misses: a machine that never runs a test again never reaps.

### The combination that actually guarantees

Layer them, because the failure classes are disjoint:

1. **Relocate** the ephemeral dir outside `home/` (fixes DOT-303's class), with a one-time sweep of old `/tmp/lima-<oldhash>` paths.
2. **Bound the run** — a timeout in the wrapper, so a hang becomes a failure with an exit code.
3. **Lease + reaper** — a lease per run, swept at wrapper start. This is the mechanism that satisfies "no VM artifact outlives its run", including after SIGKILL and reboot.
4. **Fail loudly on a dirty start** — if the reaper finds an artifact it cannot attribute to a live lease, report it and exit nonzero rather than continuing. A silently adopted orphan is how the current leak stayed invisible.

M1 stays as the fast path; it is just not the guarantee.

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
