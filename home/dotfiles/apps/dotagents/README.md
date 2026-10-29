# dotagents

Owns the machine's global agent artifacts: which agent runtimes are wired,
which sources may put skills on the machine, and the sync that installs them.

The artifacts are plain directories under `~/.agents/skills`, managed by
[dotagents](https://github.com/getsentry/dotagents). They are user-global and
every supported agent runtime loads them. The decision behind the tool choice is
in [`docs/AGENT-ARTIFACTS.md`](../../../../docs/AGENT-ARTIFACTS.md).

## What it manages

| Layer | State | Owner |
|---|---|---|
| Ansible | trust allow-list, source declarations, skill/plugin sync | this topic |
| tool | the `dotagents` binary | `apps/mise` (`npm:@sentry/dotagents`) |
| dotagents | `~/.agents/agents.toml`, `agents.lock`, `~/.agents/skills`, per-agent links | the tool |
| guard | provenance of every directory in `~/.agents/skills` | `roles/guards` |

This topic exists so the skill set is not a side effect of a coding tool's
topic. Before it, `apps/opencode` declared the sources and ran the sync, which
made an opencode install look required to get skills in any agent.

## The declaration

`defaults/main.yaml` is the manifest:

- `dotagents_agents` — the runtimes `init` wires on a fresh machine. It is
  written once, into `~/.agents/agents.toml`, because dotagents owns that file
  afterwards.
- `dotagents_sources` — approved sources with a `why` and optional `exclude`
  vetoes. Each entry becomes `dotagents trust add` and
  `dotagents add <source> --all`. Approving a source accepts everything in it,
  now and in future; `exclude` is the per-skill veto.
- `dotagents_vendored` — on-disk directories allowed without a declaration.
  Each carries a LICENSE and PROVENANCE note.

Adding a source is a trust decision. Check the licence and the publisher, give
the `why` a reason a reviewer can verify, then run the topic. The same change
must update the provenance guard's view, which is why it takes this list.

## The sync

`install.yaml` runs the pinned `dotagents` binary, not `npx @latest`. One
version on the machine is the point: the previous owner ran `@latest`, so a
plugin feature arrived in 3.4.0 while mise still pinned 3.3.0.

Order matters:

1. Probe the binary and fail with `mise install` named if it is absent.
2. Run the skills-migration guard **before** the sync. The guard catches a
   directory dotagents cannot relocate; running it after the sync guards
   nothing.
3. Initialise `agents.toml` only when it is absent, then remove the bootstrap
   skill `init` adds.
4. Trust and sync every source, then veto the excluded names.
5. Run the provenance guard **last**, so one undeclared skill cannot block the
   rest of the provision.

Re-running is idempotent. `--tags upgrade` re-runs the sync, which is the whole
skill-upgrade procedure.

## Plugin sources: what is and is not wired

`mattpocock/skills` is a plugin-marketplace repository. dotagents discovers
plugins before skills and refuses a named skill from such a source, so the
source installs as a plugin (`[[plugins]]` in `agents.toml`).

Measured on 2026-10-26:

- Plugin skills are linked into `~/.config/opencode/skills`, so opencode sees
  them in every repository.
- dotagents also publishes client marketplaces under `~/.agents/`
  (`.claude-plugin/marketplace.json`, `.cursor-plugin/`, `.github/plugin/`),
  but it does **not** point claude, cursor, codex or copilot at them. Those
  clients do not see the plugin's skills yet.
- The provenance guard audits `~/.agents/skills`; plugin skills live elsewhere,
  so they are outside that audit.

Per-client marketplace wiring is queued as its own task. Until it lands, treat
a plugin source as opencode-only and say so, rather than claiming the skill set
is uniform across agents.

## Teardown

```bash
ansible-playbook apps/dotagents/playbook.yaml --tags remove
ansible-playbook apps/dotagents/playbook.yaml --tags remove \
  -e dotagents_remove_skills=true
```

The first command removes nothing that is shared. The second removes every
skill and plugin from the approved sources and revokes their trust entries.
`agents.toml` itself is left in place: it is dotagents' state and may hold
declarations this repository does not know about.

## First run on a new machine

1. Provision chezmoi (deploys agent configs) and mise (provides node and the
   pinned dotagents binary).
2. `./run-role.sh dotagents` — or the parent playbook with `--tags provision`.
3. Check `dotagents list` and `dotagents doctor`.

`init` writes the agent list once. To add a runtime later, edit
`~/.agents/agents.toml` deliberately or run `dotagents init --force` knowing
that it deletes the skills store — the next install re-adds the declared
sources, but anything installed by hand is gone.
