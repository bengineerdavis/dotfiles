# apps/opencode — molecule scenario (default)

Confirms the **apps/opencode v2 migration end to end on a real Debian box**:
vagrant boots `debian/bookworm64` under libvirt/KVM, prepare bootstraps it to
the pre-migration state, converge runs the topic role, and the testinfra tests
assert the migration's end state. Run through the wrapper:

```bash
scripts/run-molecule.sh opencode test     # full sequence, non-interactive
scripts/run-molecule.sh opencode create   # stepwise: boot the box
scripts/run-molecule.sh opencode login    # stepwise: poke at it (needs a tty)
scripts/run-molecule.sh opencode destroy  # stepwise: tear it down
```

The wrapper (scripts/run-molecule.sh) is the supported entry point: it chdirs
here, exports the paths the role needs, installs the pinned collections, and
runs molecule through the locked `test-vm` uv group. The scenario name is
`default` per the recorded convention (TASKS.md § Planned, author decision O3).

## What it asserts (tests/test_verify.py)

| Assertion | Proves |
|---|---|
| `brew list --versions anomalyco/tap/opencode-v2` → 2.x | v2 formula installed |
| `brew list --formula anomalyco/tap/opencode` exits non-zero | v1 formula gone (and the box really had v1 — prepare installs it, so this cannot pass vacuously) |
| `opencode --version` → 2.x | the binary resolves to the brew prefix's v2 build |
| `opencode debug config` → rc 0, no normalization diagnostics, permissions array ordered (shell catch-all first, find denies after `find *`, .env asks after the read allow) | the migrated config loads — template, chezmoidata merge and `$HOME` literals all render on a real deploy path |
| `~/.agents/agents.toml` names both approved sources, five known skills exist under `~/.agents/skills/` | the dotagents skill sync converged |
| `trust.json` names `anomalyco/tap` and does not carry the v1 formula entry | tap trust present, v1 trust residue cleaned |

## Layout

- `molecule.yml` — libvirt/KVM driver, `debian/bookworm64`, 2 vCPU / 4 GB,
  the repo rsynced into the box at `/repo` so chezmoi reads the real
  templates; `ANSIBLE_ROLES_PATH` pointed at `dotfiles/` so `apps/opencode`
  and `roles/guards` resolve.
- `prepare.yml` — the bootstrap, once per box and outside the idempotence
  window: apt prerequisites, linuxbrew, mise + node LTS (matching
  `apps/mise`), chezmoi, the **v1 formula** (so the v1-gone assertions mean
  something), then the targeted `chezmoi apply --source /repo` that deploys
  the migrated config. Every task is guarded idempotent.
- `converge.yml` — imports the `apps/opencode` role directly.
- `tests/test_verify.py` — the assertions above (molecule's testinfra
  verifier runs `tests/test_*.py`; a `verify.yml` playbook would be dead
  weight under this verifier, so the plan's verify.yml became this file).

## Design decisions recorded so they are not relitigated

**Converge imports the role, not run-role.sh.** The topic's playbook hardcodes
`hosts: localhost / connection: local` — it cannot target the box without
being edited, and editing the playbook for the test's benefit changes
production behavior. Same role, same tags, same defaults; the runner differs
because the target differs (PLAN.md § Decision 3).

**The PATH bridge.** linuxbrew is not on a non-login ssh PATH, and the role's
own "Check that brew is on PATH" guard would fail a converged box. Prepare
and converge each set a play-level `PATH` with `/home/linuxbrew/.linuxbrew/bin`
first — linuxbrew's documented fixed prefix, whose value prepare owns by
installing there. The role's npx tasks carry their own mise-shims PATH
(task-level environment replaces, not merges, the play one) and do not need
brew. The testinfra tests use absolute brew-prefixed paths for the same
reason. If a verify run goes red with "brew not found"-shaped failures, check
the PATH bridge before suspecting the topic.

**molecule.yml interpolates `${VAR}`, not Jinja.** Verified against molecule
26.9.0: molecule.yml goes through a `${VAR}` env substitution, so the plan's
first sketch (`lookup('env', ...)`) would not have resolved. The wrapper
exports `MOLECULE_PROJECT_DIRECTORY`, which molecule's Config also reads for
its project directory (verified against 26.9.0), so paths resolve without
either layer hardcoding a machine-specific literal.

**The bootstrap lives in prepare, not a baked box.** A pre-baked image would
be a build; nothing here needs one. If wall-clock hurts later, baking becomes
a separate author decision (PLAN.md § prepare.yml).

**State lives in this scenario's `.molecule/`** (gitignored) because the
wrapper pins `MOLECULE_EPHEMERAL_DIRECTORY` there. Molecule 26.9.0 otherwise
keys the ephemeral directory on the project dir's basename under
`~/.ansible/tmp` — bare-molecule runs from another cwd would get a different
state than the wrapper's, and two topics' `default` scenarios would share one
state dir. Verified against 26.9.0: the env var takes precedence over both
branches of `scenario.ephemeral_directory`, and the vagrant driver's
`safe_files` keep the box env intact across prune. Always run through the
wrapper (or export the same variables) — bare `molecule` calls are the
out-of-band case the wrapper exists to prevent.

## Known risks

- **dotagents converge-twice.** The idempotence action runs converge twice;
  whether `dotagents add <source> --all`'s second run still matches
  `changed_when`'s "Added skills" was unverified at plan time. If idempotence
  goes red on the skill-sync tasks, capture the real second-run output before
  touching the topic's `changed_when` — the fix must be faithful to what
  dotagents actually prints, or the risk is reported as named rather than
  papered over (PLAN.md § The idempotence step).
- The skill set is wildcard-declared, so upstream sources can add skills
  between runs; `tests/test_verify.py` asserts the five known skills, not an
  exact set.