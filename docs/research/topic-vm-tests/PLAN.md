# Topic VM test harness — plan (molecule + Vagrant)

**Written 2026-10-11** on branch `agent/orch_sub_vplan`. Feeds the two follow-on
items in `TASKS.md` § Now: implement (`orch_sub_vimpl`) and run
(`orch_sub_vrun`). Builds on the molecule adoption approved 2026-09-14
(`TASKS.md` § Planned, "Adopt molecule for topic testing") — every decision
recorded there binds here: scenarios co-located at `apps/<topic>/molecule/`,
direct `molecule test` invocation with no pytest wrapper, pytest-testinfra as
the verifier, herdr as the first consumer, one Debian and one Darwin topic as
the done-condition, and no conversion of all 27 topics at once.

The scenario this plan designs confirms the **apps/opencode v2 migration end to
end on a Debian box** — the author's ask: "enough virtualization with vagrant
that we can inject ansible into a test box". Author rulings 2026-10-10 bind:
durable capability, not a one-off; agents may drive chezmoi and ansible on a
test box (the no-apply rule binds by reason — a Vagrant box is a separate
machine with its own HOME and its own deployed tree); the wrapper serves
humans and machines; stepwise verbs for author exploration.

## Headline decisions

| Question | Decision |
|---|---|
| Dependency install path | A uv dependency group `test-vm` in the root `pyproject.toml`, locked in `uv.lock` — the `test-llm` group pattern |
| Provider | libvirt (KVM), not VirtualBox — VirtualBox's kernel module is not loaded on this box today, and the official Debian box has dropped VirtualBox builds |
| Base box | `debian/bookworm64`, the official Debian box, current release 12.20260519.1 |
| Wrapper | `scripts/run-molecule.sh <topic> [verb]` — thin verb dispatch over molecule, the `scripts/run-bats.sh` precedent |
| Converge | converge.yml imports the `apps/opencode` role directly (not via run-role.sh — its playbook hardcodes `localhost`); slow bootstrap lives in prepare.yml |
| Config on the box | chezmoi runs on the box against the repo mounted into it — the real deploy path, permitted by the 2026-10-10 ruling |
| Scenario name | `default` (the § Planned line names `molecule/default/`); the scenario README carries the v2-migration framing |

## Machine evidence — verified locally, 2026-10-11

| Fact | Evidence |
|---|---|
| vagrant 2.4.9 at `/usr/bin/vagrant` | `vagrant --version` |
| **Vagrant is currently broken on this box**: plugin init fails with "Unable to resolve dependency: user requested 'vagrant-libvirt (= 0.12.2)'" — `vagrant plugin list` and `vagrant box list` both abort with the same error | command output, 2026-10-11 |
| VirtualBox 7.0.26 installed but **the vboxdrv kernel module is not loaded** for the running kernel (7.1.1-76070101-generic): "You will not be able to start VMs until this problem is fixed" | `VBoxManage --version` warning, 2026-10-11 |
| `/dev/kvm` present (root:kvm, current user in the group implied by the ACL) | `ls -la /dev/kvm` |
| libvirt 8.0.0 (Ubuntu build 8.0.0-1ubuntu7.21) | `apt policy libvirt-daemon` |
| Ansible core 2.21.5 via mise `pipx:ansible` | `ansible --version`; `dotfiles/apps/mise/files/config.toml:166` |
| molecule is not installed anywhere | `which molecule` → not found; `pipx list` shows only pywal and zimmify |
| vagrant-libvirt was installed at some point, pinned `= 0.12.2` | the error message above; the plugin state itself could not be read (see Not verified) |

Two of these change the plan: vagrant needs a plugin repair before anything
runs, and VirtualBox cannot start VMs until its kernel module is rebuilt —
both author-run host state (§ Author-run vs agent-run).

## Decision 1 — dependencies: a uv group, not pipx

**Add `molecule`, `molecule-plugins[vagrant]`, `pytest-testinfra` and
`ansible-core` to a new dependency group `test-vm` in the root
`pyproject.toml`** with `uv add --group test-vm ...`, following
`docs/PYTHON.md` § Dependency classes class 2. Run with
`uv run --frozen --group test-vm molecule ...`. This is the `test-llm` group
pattern already in `AGENTS.md` § Commands — a heavyweight, purpose-bound group
that stays out of the default run.

Why the uv group and not a mise `pipx:` pin:

- **docs/PYTHON.md's own rules point here.** Test-run deps live in a locked
  group; `uv run --frozen` rebuilds the environment offline from `uv.lock`.
  A `pipx:ansible`-style entry rides `version = "latest"` and churns — the
  same self-upgrade race the mise config comment records having removed once
  (`dotfiles/apps/mise/files/config.toml:123-126`).
- **One deploy ansible stays.** molecule's runtime deps (26.9.0: ansible-compat,
  enrich, jinja2, jsonschema, packaging, pyyaml, rich, wcmatch — checked on
  PyPI 2026-10-11) no longer include ansible-core, so the group must name
  `ansible-core` explicitly. That installs a second ansible-core, but only
  inside the uv environment — never on PATH, so the "two ansibles on PATH"
  concern that killed the earlier mise ansible-core backend does not apply:
  deploy runs still resolve to pipx-ansible 2.21.5 through mise.
- **The wrapper calls `uv run --group test-vm`**, so humans and agents get the
  same locked environment without a global install.

Version pins: `uv.lock` pins exact versions; the group carries floors only
(`molecule>=26.9.0`, `molecule-plugins[vagrant]>=26.9.28`,
`ansible-core` — pick the floor the scenario is proven against, excluding
ansible-core 2.17.x per the CVE-2026-11332 exclusion molecule itself adopted in
v26.8.0). The ansible-core pin decision is small but real: molecule v26.8.0
excluded 2.17.x for a CVE, so the floor should be ≥ the first non-affected
release. Confirm the exact floor on implementation day.

Collections: the vagrant driver requires the **`community.vagrant` collection
(≥ 1.0.1)** — read from the driver source
(`molecule_plugins/vagrant/driver.py`, `required_collections`), fetched
2026-10-11. The scenario also uses `community.general` (already pinned 13.0.1
in `dotfiles/requirements.yml`). The wrapper ensures collections are installed
(`ansible-galaxy collection install -r dotfiles/requirements.yml` is idempotent
and skips what is present) and exports `ANSIBLE_COLLECTIONS_PATH` so the uv
env's ansible-core sees the user-level collection directory. Adding
`community.vagrant` to `dotfiles/requirements.yml` itself is an author
decision (§ Open author decisions) — that file is the captured state and O1
makes every pin a deliberate re-grade.

Not adopted: `pytest-molecule` and `pytest-ansible` — already rejected with
evidence in the § Planned correction (pytest-molecule archived 2023;
pytest-ansible EOL December 2026 with a published migration table). Nothing
here changes that.

## Decision 2 — provider: libvirt; box: debian/bookworm64

**libvirt (KVM) is the provider.** Three independent reasons:

1. **VirtualBox cannot start VMs on this box today** — the vboxdrv module is
   not loaded for the running kernel (verified 2026-10-11). Fixing it needs
   `sudo /sbin/vboxconfig`, author-run host state, and re-breaks at every
   kernel update (this box tracks a rolling system76 kernel).
2. **The official Debian box no longer publishes VirtualBox builds.**
   `debian/bookworm64`'s current version 12.20260519.1 (created 2026-05-19)
   ships a libvirt provider only; the last virtualbox build was
   12.20250126.1 (2025-01-26). Picking VirtualBox would freeze the scenario on
   a year-old box build. Vagrant Cloud API fetched 2026-10-11.
3. **KVM is already working**: `/dev/kvm` is present and libvirt 8.0.0 is
   installed. KVM also converges faster than VirtualBox emulation, which the
   brew-and-node bootstrap needs (§ Cost).

The vagrant-libvirt plugin was installed at some point (the `= 0.12.2` pin in
the failed resolution) but vagrant currently cannot resolve it. **Step 0 of
implementation is `vagrant plugin repair`** (or `vagrant plugin expunge
--reinstall`), author-run — it modifies `~/.vagrant.d`, host machine state.
Success test: `vagrant plugin list` runs clean and shows vagrant-libvirt
0.12.2; `vagrant box list` runs clean. Compatibility of vagrant-libvirt 0.12.2
with libvirt 8.0.0 was unverified at plan time — settled by the confirmation
run, which rode that pair through every phase (§ Not verified, Settled).

**Base box: `debian/bookworm64`** (official Debian org, 84,295 downloads,
current release 2026-05-19, libvirt/amd64 with sha256 checksum published).
Alternative considered and rejected: `generic/debian12` — broader provider
coverage but stale (current release 4.3.12 created 2024-01, Debian 12.4.0;
last updated 2024-10-13), so it ships old packages the scenario would then
upgrade, which is slower and less representative. Vagrant Cloud API fetched
2026-10-11. The real migration targets a Debian 12 machine, so bookworm is the
right approximation.

Sizing: 2 vCPU, 4 GB RAM, 15 GB disk. opencode-v2 installs from a bottle (no
compilation), so disk is dominated by the linuxbrew checkout and node — 15 GB
leaves slack. RAM 4 GB because brew's Ruby and npm both run inside the box
while nothing else does.

macOS is out of scope for VM testing and the plan says so plainly: no macOS
Vagrant boxes exist (recorded in the § Now line, 2026-10-06). The Darwin leg
of the molecule done-condition needs a different mechanism and stays open in
the § Planned item.

## Decision 3 — scenario layout

```
dotfiles/apps/opencode/
  molecule/
    default/
      molecule.yml      # driver, platform, provisioner env, verifier
      prepare.yml       # apt deps, linuxbrew, mise+node, chezmoi, v1 formula
      converge.yml      # imports the apps/opencode role against the box
      verify.yml        # testinfra assertions — the migration's end state
      README.md         # what the scenario is (the v2 migration confirmation)
```

This sits inside the topic per the co-location rule — `docs/TOPICS.md` §
Per-topic changelog makes the argument that travels with the directory is what
survives the move, and the § Planned decision recorded the same placement for
scenarios. A later `topic tests live with the topic` migration picks these up
for free.

### molecule.yml

```yaml
dependency:
  name: galaxy
driver:
  name: vagrant
  provider:
    name: libvirt
platforms:
  - name: opencode-bookworm
    box: debian/bookworm64
    memory: 4096
    cpus: 2
    instance_raw_config_args:
      # Sync the repo (the worktree molecule ran from) into the box so
      # chezmoi on the box reads the real templates. Path rendered per-run.
      - "vm.synced_folder '{{ lookup(\"env\", \"MOLECULE_PROJECT_DIRECTORY\") }}/..', '/repo', type: 'rsync'"
provisioner:
  name: ansible
  env:
    ANSIBLE_ROLES_PATH: "{{ lookup('env', 'MOLECULE_PROJECT_DIRECTORY') }}"
  inventory:
    host_vars:
      opencode-bookworm:
        ansible_python_interpreter: /usr/bin/python3
verifier:
  name: testinfra
```

Notes on the non-obvious parts:

- **`ANSIBLE_ROLES_PATH` set to the project directory is what makes the role
  and its guards resolve.** The role's tasks import `roles/guards` by name,
  which `docs/TOPICS.md` § Shared guards says resolves relative to the working
  directory — the same constraint `ansible.cfg` and `run-role.sh` are under.
  The wrapper chdirs to `dotfiles/` (§ Decision 4), so
  `MOLECULE_PROJECT_DIRECTORY` is `dotfiles/`, and `apps/opencode` and
  `roles/guards` both resolve from there. This is the scenario's answer to
  run-role.sh's cwd dependence: same root cause, same fix — run from
  `dotfiles/`.
- **molecule.yml is Jinja-rendered**, so `lookup('env', ...)` works for paths
  that must not be hardcoded. Machine-specific values are resolved at run
  time by the layer that owns them — same rule as chezmoi templates, same
  silent-failure risk if it were a literal. That molecule.yml renders Jinja
  is common practice but must be confirmed against molecule 26.x on
  implementation day (§ Not verified).
- **`find_vcs_root()` recognizes git worktrees as of molecule 26.9.0**
  (release notes, PR #4640) — the repo's worktree-per-session workflow would
  otherwise confuse molecule's project-root discovery. Pin ≥ 26.9.0 for this
  reason alone.
- `create.yml`/`destroy.yml` are **not** written: the driver's default
  playbooks (fetched from molecule-plugins main, 2026-10-11) boot the box with
  `community.vagrant.vagrant` and dump the instance config — exactly right.
  Override them only when a real need appears; every overridden default is a
  second place to be wrong.

### prepare.yml — the bootstrap

Runs once per box, before converge, and is deliberately outside the
idempotence check (molecule's idempotence action runs converge twice, not
prepare). Content, in order, each guarded idempotent:

1. **apt packages** (`become: true` per task): `curl`, `git`, `build-essential`,
   `file` — linuxbrew's documented prerequisites
   (docs.brew.sh/Homebrew-on-Linux).
2. **linuxbrew** to `/home/linuxbrew/.linuxbrew` via the official install
   script, run as the vagrant user (the script needs sudo for one directory
   creation, which the vagrant user has passwordless). Then export
   `PATH=/home/linuxbrew/.linuxbrew/bin:$PATH` for subsequent tasks via the
   play environment — brew is not on a non-login shell's PATH by default, and
   the topic's own guard (`apps/opencode/tasks/install.yaml`, "Check that brew
   is on PATH") would otherwise fail.
3. **mise + node LTS** via mise's install script, then `mise use -g node@lts`
   — matching how the real box gets node (the `apps/mise` topic, which
   `topic_requires: [homebrew, node]` in `apps/opencode/topic.yml` resolves
   to).
4. **chezmoi** via `brew install chezmoi`.
5. **The v1 formula**: `brew install anomalyco/tap/opencode` plus the tap and
   trust steps it needs. This reproduces the pre-migration state so the
   converge's "v1 gone" assertion means something — a box that never had v1
   would pass it vacuously, which is the "test that passes without exercising
   what it claims" failure `spec.md` § Verification exists to stop. The
   prepare installs only the formula, not the topic's v1-era config.

**The scenario bootstraps rather than requiring a precondition box.** Reasons:
a pre-baked box is a build (packer templates, image registry, drift) — the
build ladder says outsource or refuse, and nothing here needs it; the
bootstrap is plain configuration; and prepare sitting outside the idempotence
window absorbs its slowness. If wall-clock later hurts, baking a box becomes a
separate author decision, not a default.

### converge.yml

```yaml
- name: Converge
  hosts: all
  become: false            # mirrors apps/opencode/playbook.yaml (become: false)
  roles:
    - role: apps/opencode
```

**converge imports the role directly, not run-role.sh.** Two reasons:

- `apps/opencode/playbook.yaml` hardcodes `hosts: localhost,
  connection: local` — it cannot target the box without being edited, and
  editing the playbook for the test's benefit changes production behavior.
- The role is the single source of truth for what install does
  (`tasks/main.yaml` routes the lifecycle tags; the playbook is a two-line
  wrapper around it). Importing the role exercises exactly the task files the
  migration changed, with the same tags. The TASKS.md run item's "run-role
  path for apps/opencode" is satisfied in substance: same role, same tags,
  same defaults — the runner differs because the target differs. This is
  recorded in the scenario README so nobody relitigates it.

`become: false` mirrors the topic playbook: the homebrew module refuses to run
brew as root and the topic never needs root. Prepare carries the per-task
`become: true` where apt needs it.

### verify.yml — the assertions

Testinfra (the § Planned choice), molecule's ansible connection, `hosts: all`.
The migration's end state, each assertion naming what proves it:

| Assertion | Command / check |
|---|---|
| v2 formula installed | `brew list --versions anomalyco/tap/opencode-v2` returns a 2.x version |
| v1 formula absent | `brew list --formula anomalyco/tap/opencode` exits non-zero (brew's own "Formula not installed" exit) |
| `opencode` resolves to the brew binary, reports 2.x | `opencode --version` output starts with `2.` |
| The migrated config loads | `opencode debug config` exits 0, stderr carries no normalization diagnostics, and the JSON output contains the `permissions` array with the shell allow-list in order (catch-all first, `find` denies after `find *`) |
| Skills synced | the five manifest skills exist under `~/.agents/skills/`, and `~/.agents/agents.toml` exists |
| Tap trust present | `~/.homebrew/trust.json` (or `$XDG_CONFIG_HOME` variant) names `anomalyco/tap` |

Brew-on-box PATH caveat: verify's commands run in a non-login shell over ssh,
so brew is not on PATH — assertions either use the absolute
`/home/linuxbrew/.linuxbrew/bin/brew` or prepend the PATH in the test
fixture. Flagged so the first red verify run is not mistaken for a topic bug.

## Decision 4 — the wrapper: `scripts/run-molecule.sh`

```bash
scripts/run-molecule.sh <topic> [verb] [extra molecule args...]
# verbs: create | prepare | converge | idempotence | verify | login |
#        destroy | test (default)
```

- **Lives in `scripts/`, not `bin/`.** `bin/` scripts are chezmoi-deployed
  user tools; `scripts/` holds repo-process tooling — `run-bats.sh` is the
  precedent. This wrapper is not a user tool and must not be deployed to
  other machines.
- **Chdirs to `dotfiles/`** before invoking molecule, so
  `MOLECULE_PROJECT_DIRECTORY` lands where `roles/guards` and `apps/` resolve
  (§ Decision 3). run-role.sh's cwd dependence is the known trap; the wrapper
  removes it rather than documenting around it.
- **Runs molecule through `uv run --frozen --group test-vm`** so humans and
  machines get the identical locked environment.
- **Verb mapping is thin**: `<topic> <verb>` →
  `molecule <verb> -s default -d vagrant` from the scenario's parent. `login`
  passes through untouched — it needs a tty and is human-only. Everything else
  is non-interactive; `molecule test` already exits non-zero on failure with
  no tty assumptions, which is the machine mode. Extra args pass through
  (`-- --destroy=never` for an author who wants to linger).
- **Stepwise verbs serve the author's exploration flow directly**: `create`
  then `login` gives a provisioned box to poke at; `converge`/`verify` re-run
  against a live box without recreating it; `destroy` tears it down. Machine
  mode is the default `test` verb.
- **Build-ladder justification** (the task asks for it explicitly): this is
  the `run-bats.sh` case, not a build. Molecule is the tool; the wrapper is
  an interface to it — argument dispatch, one chdir, one env export, no logic
  of its own, sized well under the bash 80-100-line rule. The alternative
  (documenting raw molecule invocations) fails the human-mode requirement:
  the cwd + uv + collections setup is exactly the setup a human forgets, and
  the author asked for a wrapper that brings up the right-provisioned
  environment automatically.
- **pytest coverage for argument handling** belongs to the implement item
  (`orch_sub_vimpl` already names it), at `tests/run_molecule/` per the house
  layout.

## Decision 5 — config on the box: real chezmoi, mounted repo

**The scenario runs chezmoi on the box against the repo synced into it**, per
the 2026-10-10 ruling that agents may drive chezmoi on a test box. Prepare
runs `chezmoi init --source /repo --apply ~/.config/opencode` (the targeted
apply the v2 PLAN's author-run step 3 uses). This tests the real deploy path
— the template, the chezmoidata merge, the `$HOME` literals — rather than a
hand-placed copy that could silently differ from what the author's machine
will get. That is the whole point of "confirm we're good for the migration".

Fallback if the synced folder fights the driver (rsync inside the box,
Jinja path rendering): prepare clones the repo from origin at the branch
under test instead. Cheaper to debug, but tests a checkout rather than the
working tree — named so the implementer picks deliberately if it comes to
that.

## The idempotence step — risks found before implementation

The § Planned standard is molecule's `idempotence` action: converge runs
twice, the second must report no changes. Task-by-task read of
`apps/opencode/tasks/install.yaml` as it stands:

| Task | Second run | Risk |
|---|---|---|
| `brew trust --tap` | "Already trusted tap", `changed_when` handles it | none |
| `homebrew_tap` present | no-op | none |
| v1 uninstall `state: absent` | no-op once v1 is gone | none |
| `brew untrust --formula` v1 | "Not trusted", `changed_when` handles it | none |
| v2 install `state: present` | no-op | none |
| dotagents `trust add` | exits non-zero "already in", filtered | none (existing code) |
| dotagents `add <source> --all` | re-add refreshes the install — **but whether the second run's output still matches `changed_when`'s "Added skills" is unverified** | **the one real risk** |
| dotagents veto `remove -y` | "not found" path filtered | none |
| approved-sources guard | runs real (not check mode) | none on a fresh box |

The dotagents re-add is designed idempotent in *outcome* (README: "Re-running
the add refreshes the installation"), but idempotence here depends on the
*reported* change, and its second-run output has never been observed. The
implement item should capture that output before assuming; if it reports
"Added skills" on a refresh, the fix is a `changed_when` refinement, not a
scenario skip.

Two structural points keep the rest out of the window: the whole machine
bootstrap (apt, linuxbrew, mise, chezmoi, v1 formula) lives in prepare, which
the idempotence action does not run; and nothing in converge creates state
outside the role, so the check measures the role alone — which is the thing
being tested.

The `idempotence` action itself: present throughout the molecule release
notes v25.9.0 → v26.9.0 (fetched 2026-10-11, no removal or rename appears);
confirm with `molecule idempotence --help` at install time — a one-second
check that closes the gap.

## Destroy safety and cost

**The scenario must never touch the host.** Enumerated:

- Every role and prepare task targets the box (`hosts: all` over ssh);
  molecule's create/destroy playbooks run on localhost but only call vagrant.
- No host package manager, no host `~/.config`, no host chezmoi apply. The
  agents-never-apply rule is untouched: the box is a separate machine and the
  ruling names it as such.
- The only shared host state is the ansible collections directory
  (`~/.ansible/collections`), which the wrapper may install into. It is
  user-level, additive, and already exists for pipx-ansible — recorded rather
  than hidden.
- `~/.vagrant.d` plugin state is author-managed (step 0); nothing in the
  scenario writes it.

**Recovery**: `molecule destroy` (and the wrapper's `destroy` verb) is
idempotent — a crashed session's residue is cleaned by re-running it;
`vagrant global-status --prune` handles stale libvirt domain records if
vagrant loses track. A box that survived a crashed run is safe to reuse only
via create→converge, since prepare's guards make every step re-runnable.

**Cost — measured** by the confirmation run (2026-10-17, `orch_sub_vrun`).
The estimates that stood here before any VM existed are kept below the table
for context; every one of them ran long — the real harness is roughly 5-10x
cheaper than planned (total estimate ~25-50 min, measured ~4.6 min).

| Measurement | Value |
|---|---|
| `create` verb = boot + prepare (molecule 26.x runs its whole create_sequence — see note) — fresh box, cached image | 205.5 s and 211.1 s (two fresh-box runs) |
| — boot + repo rsync (create play) | ~32 s |
| — prepare bootstrap (prepare play) | ~178 s |
| converge | 34.1 s |
| idempotence (second converge) | 15.5 s — `changed=0` |
| verify (testinfra) | 5.7 s — `6 passed` |
| destroy | 16.3 s and 15.7 s (two runs) |
| stepwise sum (create+converge+idempotence+verify+destroy) | 277.1 s |
| full `test` verb, fresh box, one command | 273.9 s — `6 passed in 2.40 s` |

Conditions, as the run item's done-condition requires: box
`debian/bookworm64` 12.20260519.1 (libvirt provider, KVM; the 1.2 GiB image
was cached from the implement run — the first-download time is NOT measured);
2 vCPU, 4 GiB RAM confirmed inside the domain; molecule 26.9.0,
molecule-plugins[vagrant] 26.9.28, pytest-testinfra 10.2.2, ansible-core
2.21.5 (locked `test-vm` group), vagrant 2.4.9 + vagrant-libvirt 0.12.2,
libvirt 8.0.0. Host context: 32 cores, 31 GiB RAM, load ~1.1, no ollama model
resident, no other VM running; root filesystem at 99% (9.8 GiB free) — one
box fits, concurrent runs or a baked image would not.

Prepare internals, from task-start timestamps: apt ~81 s, `brew install
chezmoi` ~47 s, v1 formula ~16 s, linuxbrew ~16 s, mise ~3 s, node ~7 s, tap
steps ~3 s, uv + skill-trust ~2 s, the targeted chezmoi apply ~4 s. The
boot/prepare split comes from `ANSIBLE_LOG_PATH` timestamps — ansible-core
2.21's `profile_tasks` callback emits nothing, tried both through molecule
and on a direct playbook run (2026-10-17).

Two facts the run surfaced about the harness itself:

- **The `create` verb includes prepare.** Molecule 26.x's create_sequence is
  dependency → create → prepare, so a fresh `create` is boot + bootstrap,
  not boot alone. Per-phase boot-only timing needs the log-timestamp method
  above; a fresh-box `prepare` re-run (guards skipping) was not measured.
- The plan's "15 GB disk" sizing never came into play: the box ships its own
  100 GiB virtual disk, sparse — 3.85 GiB actually allocated after
  prepare + converge. molecule.yml sets cpus and memory only.

Disk, measured: 1.2 GiB box image cached under `~/.vagrant.d`, ~3.9 GiB
allocated to the domain's sparse overlay after a full run. One box at a
time; concurrent sessions must claim the topic before running VM tests,
since molecule's ephemeral state lives inside the topic directory —
`.molecule/` is on the ignore list as of implementation.

Estimates before the first run, kept for the record:

| Phase | First run | Re-run (cached box, prepared) |
|---|---|---|
| Box download + boot | 5-10 min | 1-3 min |
| prepare (apt, linuxbrew, mise+node, chezmoi, v1) | 10-20 min | 2-5 min |
| converge | 5-10 min | 3-6 min |
| idempotence + verify | 5-10 min | 3-6 min |
| **total** | **~25-50 min** | **~10-20 min** |

## Author-run vs agent-run split

| Step | Who | Why |
|---|---|---|
| `vagrant plugin repair` (step 0) | author | modifies `~/.vagrant.d` — host machine state |
| uv group addition, scenario files, wrapper | agent (implement item) | repo state, ordinary branch work |
| `molecule create/converge/verify/test/destroy` against the box | agent or author | the ruling: the box is a separate machine; create and destroy bound the blast radius |
| `molecule login` exploration | author | needs a tty; the stepwise flow exists for them |
| `sudo /sbin/vboxconfig` | nobody, unless VirtualBox is later chosen | host kernel state; libvirt makes it unnecessary |

## Open author decisions

SETTLED 2026-10-11, all four, by the author after this plan was written:

1. **O1 — `community.vagrant` in requirements.yml: add, pinned** (plan
   default). The deployed ansible toolchain can drive vagrant directly.
2. **O2 — version policy for the `test-vm` group: pin exact** (plan
   default). Bumps are deliberate re-locks.
3. **O3 — scenario directory name: `default`** (the recorded § Planned
   convention wins over the self-describing alternative).
4. **O4 — the vagrant repair: agent-run, done 2026-10-11.**
   `vagrant plugin repair` failed with the same unresolved pin;
   `vagrant plugin uninstall vagrant-libvirt && vagrant plugin install
   vagrant-libvirt` succeeded and reinstalled the SAME 0.12.2 — the
   unresolved pin was stale plugin state, not a version problem.
   Verified after: `vagrant plugin list` clean (vagrant-libvirt 0.12.2
   global), `vagrant box list` clean, vagrant 2.4.9 current. The
   original text of each decision follows, kept for the record.

1. **`community.vagrant` in `dotfiles/requirements.yml`?** The driver requires
   it; adding it there (pinned) makes it deploy-repo state under O1 — a pin is
   a deliberate re-grade. Alternative: install it ad hoc from the wrapper,
   unpinned. Recommended: requirements.yml, for the same reason the file pins
   everything else.
2. **Pin versions or ride the lock?** The group's floors go in
   `pyproject.toml`; `uv.lock` pins exactly. The pin-bump habit
   (`docs/REFERENCES.md` quarter-boundary) applies. Default: floors in the
   group, lock pins the rest, no extra ceremony.
3. **Scenario name `default` vs `v2-migration`.** The § Planned line names
   `molecule/default/`; the plan follows it. One `git mv` renames if the
   author prefers the semantics.
4. **Vagrant plugin repair now?** Without it, nothing runs (verified broken
   2026-10-11). It is one command, author-run, reversible.

## Not verified

Named plainly, per `spec.md` § Evidence. Settled items moved out below with
what settled them; the remainder stay open.

### Still open

- **The author's interactive login flow** — `molecule login` needs a tty;
  agent runs do not have one. Closes the first time the author steps through
  create → login → inspect → destroy.
- **The Darwin leg** — no macOS Vagrant boxes exist; a different mechanism
  is needed and stays open in the § Planned item.
- **The first-create box download time** — the 1.2 GiB image was already
  cached for the confirmation run; forcing a re-download buys one number at
  the cost of 1.2 GiB egress, so it stays unmeasured. Closes the next time a
  box cache is cold (a new machine, an upgraded box version).
- **The real-machine apply** — the author runs the actual migration on the
  real box per the v2 migration plan; the harness confirms the Debian leg on
  a disposable VM, not the author's machine state.

### Settled

- **Vagrant plugin repair outcome** — settled 2026-10-11 (§ Open author
  decisions, O4): the pin was stale plugin state; uninstall + reinstall of
  the same 0.12.2 fixed it.
- **vagrant-libvirt 0.12.2 ↔ libvirt 8.0.0 compatibility** — settled by the
  confirmation run 2026-10-17: every phase ran on that pair.
- **Box file size and rsync inside the box** — settled by the confirmation
  run: 1.2 GiB image; prepare installs rsync and the synced `/repo` fed both
  the skill-trust install and the chezmoi apply.
- **molecule.yml interpolation** — settled by the implement run: the plan's
  Jinja sketch was wrong, molecule 26.x interpolates `${VAR}` (corrected in
  the scenario files and README).
- **Per-scenario `provisioner.env` / `ANSIBLE_ROLES_PATH` with the vagrant
  driver** — settled by the implement and confirmation runs: converge
  resolved `apps/opencode` and `roles/guards` on the box.
- **dotagents' second-run `add --all` output** (§ The idempotence step — the
  plan's one real risk) — settled by the confirmation run: the idempotence
  converge reported `ok=16 changed=0`, the sync task reporting no change.
  No `changed_when` refinement needed.
- **`community.general.homebrew`'s brew discovery on a linuxbrew default
  path** — settled by the confirmation run: the role's brew guard passed
  under the PATH bridge.
- **`opencode debug config` in a non-tty context** — settled by the
  confirmation run: rc=0 over the ansible ssh connection, stderr empty.
- **All wall-clock figures** — settled by the confirmation run: § Cost,
  measured table.
- **The exact ansible-core floor** (2.17.x CVE exclusion) — settled by the
  implement run: 2.21.5 locked in `uv.lock`.
