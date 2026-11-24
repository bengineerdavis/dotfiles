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
  `dotagents add <source> --all`. A plugin source installs its plugins rather
  than a wildcard skill set. Approving a source accepts its published
  artifacts; check the upstream manifest and hooks before changing the list.
- `dotagents_plugin_targets` — complete declarations for plugins that cannot
  serve every configured runtime. Ansible manages only this named TOML block.
  Dotagents owns and validates the rest of `agents.toml`.
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

`mattpocock/skills`, `UditAkhourii/adhd`, and `ayghri/i-have-adhd` are plugin
sources. Dotagents discovers plugins before skills and refuses a named skill
from a plugin source. `--all` therefore installs a plugin, not a wildcard skill.

Verified with isolated home directories and dotagents 3.4.0 on 2026-11-15:

- Dotagents links plugin skills into `~/.config/opencode/skills`.
- This topic registers generated marketplaces with Claude and Codex and
  installs the declared plugins into them.
- Dotagents writes Cursor marketplace files, but this topic does not register
  them with Cursor. Generated files do not prove client activation.
- Copilot and VS Code need a case-by-case compatibility check. An absent skill
  link is not an implicit pass.
- The provenance guard audits `~/.agents/skills`. Plugin skills live under
  `~/.agents/plugins/<name>/`, so they are outside that audit.

Per-client marketplace wiring:

- `claude` and `codex` are wired by this topic — `claude plugin marketplace
  add` plus `claude plugin install`, and `codex plugin add` — reading the
  plugin names from the marketplace file dotagents generated.
- `cursor` is excluded: its CLI exposes no plugin or marketplace subcommand
  (checked 2026-10-30, cursor 3.27.22).
- **A client whose CLI is absent is skipped, not failed.** The clients are
  machine-local, and `claude` comes from `apps/claude-code`, which is
  Darwin-only (Debian is DOT-141). The skill set still reaches every agent
  through `~/.agents/skills`. A client that IS installed and then fails for a
  real reason still fails the run.
- Set `dotagents_wire_claude` or `dotagents_wire_codex` to `false` to decline
  wiring for an installed client. The run reports it as *declined*, which is
  distinct from *absent*, so the two states never blur.

### The ADHD skill boundary

`UditAkhourii/adhd` supplies its canonical `skills/adhd/SKILL.md`. Its preflight
rules gate the roughly ten parallel Agent calls and state their cost. This
topic does not install the optional `adhd-agent` CLI or invoke the skill.

`ayghri/i-have-adhd` contains `hooks/hooks.json`. Dotagents 3.4.0 rejects that
bundle for Copilot rather than dropping unsupported resources. The author
approved excluding Copilot for this plugin on 2026-11-15. Copilot stays enabled
for other sources, and the exclusion is not reported as a successful install.

OpenCode receives the canonical `i-have-adhd` skill in A. Dotagents does not
link the repository's `.opencode/plugins/*.mjs` setup hook or
`.opencode/command/i-have-adhd.md` command. The setup hook registers a context
hook when OpenCode loads it; always-on injection remains opt-in. DOT-349 owns
that hook, the slash command, and its teardown. Do not mark B complete merely
because the skill link exists.

### Upstream references

- [Dotagents plugin configuration](https://github.com/getsentry/dotagents/blob/main/plugins/dotagents/skills/dotagents/references/config-schema.md#plugins-section)
  documents per-plugin `targets`. The 3.4.0 CLI does not expose an exclusion
  flag, so Ansible manages the named declaration before each refresh.
- [Dotagents native activation proposal](https://github.com/getsentry/dotagents/pull/178)
  is open. Recheck it before expanding client wiring.
- [ADHD installation](https://github.com/UditAkhourii/adhd/blob/main/documentation/install.md)
  documents the canonical skill and the separate optional CLI.
- [i-have-adhd installation](https://github.com/ayghri/i-have-adhd/blob/main/INSTALL.md)
  documents its native OpenCode adapter. DOT-349 also owns the upstream
  contribution decision; no issue or pull request is published implicitly.

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
