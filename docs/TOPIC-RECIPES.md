# TOPIC-RECIPES — reusable decision tables for creating topics

These are the settled decisions from building a topic, generalized so the next
one does not re-derive them. Explanations, not authority: `docs/TOPICS.md`
and root `spec.md` carry the binding rules, and this file links to them instead of
restating. Settled 2026-09-18/19, instance: the `herdr` topic
(`home/dotfiles/apps/herdr/README.md` records that instance and links back here).

This file is queued as input to the normative topic spec (TASKS.md § Now): the
spec session lifts what belongs in spec terms and records any reasoned rejection.

## Recipe: docs and galaxy first — the module-vs-shell ladder

Standing rules (author, 2026-09-19): check the docs and the galaxy for an
established solution before hand-rolling anything; third-party collections
and roles ARE allowed — gated by the **support grade** below, never by vibes;
always record the grade when adding a dependency; always ask before adopting
anything below grade A; always ask before falling back to shell/cmd, naming
the module search that came up empty.

### The support grade (four checks, all verifiable offline from the installed copy)

| # | Check | How to verify |
|---|---|---|
| 1 | **Maintained** | Named maintainer(s) in the module docstring, and recent upstream activity touching the module or its utils — changelog entries in the collection's `changelogs/changelog.yaml` within ~12 months |
| 2 | **Tested** | The collection ships an integration target: `tests/integration/targets/<module>/` exists in the installed tree |
| 3 | **Supported tier** | Not marked for removal or orphaned: no entry in the collection's `meta/runtime.yml` removals/redirects, no "unsupported" note in `ansible-doc` output |
| 4 | **Interface honesty** | `check_mode` documented in the module's ATTRIBUTES, and a source read of what it actually runs and mutates (docstrings lie; the launchd "privileged" note hid that it runs unprivileged and finds per-user plists first) |

For **roles** (vendored playbook code — weigh heavier than modules): the same
four minus #2, substituted with "the role carries its own tests or is
trivially thin", plus a **license check** and a bias toward collections — a
role is vendored into every run.

### Adoption matrix

- **Grade A — all four pass.** Adopt. If it is a NEW collection/role for this
  repo, record the grade with the evidence lines (the four checks' results)
  in the adopting topic's CHANGELOG — the record is the gate, nothing silent.
  Already-declared collections (`community.general` here) with a module
  passing all four need no ceremony.
- **Grade B — three of four, or a check is unverifiable offline.** Ask the
  author, citing which check failed and the evidence you do have.
- **Grade C — two or fewer, or marked unsupported.** Do not adopt; use a
  ratified shell fallback or route the need elsewhere.

Worked example (2026-09-19): `community.general.launchd` — maintainer named,
two launchd changelog entries in the current release, integration target
present, no removal entry, check_mode full → grade A; adopted for the herdr
topic with no new galaxy dependency (the collection was already declared).

### When no module fits

Justified-by-construction fallbacks: third-party/first-party CLI invocations
(`herdr`, `mise use`/`mise unuse`, `mise upgrade`) — a wrapper module would
exec the same binary with less transparency. Probes are the grey zone — a
`stat` beats a `systemctl cat`; a content probe has no module (`grep -q` is
the honest floor). Ratified fallbacks get a one-line comment citing the
author's ruling and date.

### Extension after adoption

Once a topic is adopted, extending it with additional shell commands is
allowed **without a fresh ask per command**, when both hold:

1. **No module support exists** for the task — the ladder above is still
   checked first, and the new command gets the same one-line comment citing
   this rule.
2. **It makes the topic durable** — it serves the topic's ability to do its
   job reliably: converge, stay idempotent, survive upgrades and removals.
   Durability is the gate, not convenience: an extension that adds state
   still owes its teardown counterpart in the same change (spec.md §
   Layering), and an extension a module already covers is not durable, it is
   a regression to hand-rolled.

The ask-per-command rule keeps its force for anything before adoption and
for any new galaxy dependency at any time.

## Recipe: choosing an install mechanism

Two questions decide it: **which machines run it** and **who upgrades it**.

| Mechanism | Choose when | Who upgrades | Gotchas |
|---|---|---|---|
| Homebrew formula | Official formula exists; Darwin-only fleet | System role (`apps/homebrew`) | Debian coverage only via linuxbrew; a daemon installed through linuxbrew is odd. `topic_requires: [homebrew]` resolves on Debian through the probe alias (`roles/topic-resolution`) |
| Apt repository | Upstream publishes a signed repo; Debian-native | System role (`apps/apt`) | Needs `become: true`; verify the key before use, never trust blind; URL path *and* suite can change per channel (claude-code precedent) |
| mise entry | Cross-OS GitHub-release CLI; per-user is fine | `mise upgrade` (apps/mise upgrade tasks) | The entry lives in `apps/mise/files/config.toml`, which is a listed cross-session hazard. Follow the `github:` backend convention there — never `ubi:` |
| Release artifact | Full topic control; no manager carries it | The topic itself, `[install, upgrade]`-tagged with checksums | Verify checksums are actually published before choosing; v0.x churn means frequent bumps |
| npm/pipx/cargo | Part of an existing mise-managed family | `mise upgrade` | Belongs in `apps/mise/files/config.toml`, not a private install; declare the dependency, do not install directly |

**Runtime+config bundles.** A tool that is a binary *plus* a service *plus*
config is still one topic; the mechanism table decides only the binary.

**Tool-entry ownership via first-party commands** (settled with herdr): a topic
may own its own entry in the global mise config by running
`mise use -g <tool>` on install and `mise unuse --global <tool>` on remove,
probe-first so the command is a no-op once converged. The global config is a
regular chezmoi-managed copy: those commands change the deployed file, not the
tracked source. A subsequent apply can overwrite that drift, so capture the
entry deliberately before applying. DOT-240 owns the capture-trigger design;
until then, the owning topic must not treat `mise use -g` as a committed capture.
This is the exception to "topics never write other topics' files" — it works
because mise itself owns the file format and the topic claims the entry as its
own state, probe-first. See the mise hazard line in AGENTS.md § Cross-session
hazards.

**Never self-update a manager-installed tool.** Some tools ship their own
updater (`herdr update`) which is valid only for direct installs; brew, mise
and nix installs must be upgraded through their manager. The topic must not
shell out to the self-updater; note it in the README so nobody "fixes" it later.

## Recipe: the shared-catalogue pattern

When several topics need the same list of things — extensions, integrations,
agents — the list is a **catalogue**: `home/dotfiles/config/<domain>.yaml`, plain
data the playbook and topics read. Precedent: `home/dotfiles/config/editors.yaml`.

The threshold for earning a new catalogue file (all four must hold):

1. A distinct domain of shared truth exists — a new *kind*, not more of the same.
2. A subscriber exists or its wiring is queued — no speculative catalogues.
3. The truth is domain-owned, not topic-private — one topic's private wants
   stay in that topic's own defaults.
4. It cannot join an existing catalogue without mixing domains.

Fold-back: when a catalogue's last subscriber goes, the file goes with it.

Schema shape (see editors.yaml for the worked example): entries with an `id`
spelled exactly as the consuming tool spells it, a required `why`, optional
scoping, and **dated verdicts** as the recorded evidence — a verdict is
evidence for scope, not a second switch. Keep an explicit `*_ignored` list for
what the installs will produce or refuse but which is not an entry, so an
id-diff drift report does not read drift forever.

Consumption today is an **interim role-relative direct read**
(`vscode_catalogue_path: "{{ role_path }}/../../config/editors.yaml"` is the
shape), because the topic must land on the same file whether the parent
playbook or `run-role.sh` runs it. The destination is `topic_subscribes` +
playbook resolution + injected slice (queued in TASKS.md § Planned, gated on
the normative topic spec) — when that machinery lands, the direct read is
replaced with a behavior-preserving no-op switch proven by `--check` converge.

A topic consuming a catalogue runs a **thin install-and-report loop**: list
what is installed, compute the missing set, install it with
`failed_when: false`, collect failures, report a verdict line per entry, and
fail once at the end naming everything unresolved. Teardown is **gated**
(default-off opt-out var) and uninstalls only the **intersection** of what the
catalogue claims and what is actually installed — never everything installed,
because the machine may hold things the topic does not own.

## Recipe: integration vs dependency — skip vs raise

A tool often needs *another* tool at runtime (a provider, an agent CLI it
hosts). Two different failure modes, deliberately not the same:

- **The consumer tool is absent** (never installed, or the user declined it):
  **skip-and-report**. The integration phase runs only after install; it never
  fails the run, and it reports what it did not do and why.
- **A required provider is absent or fails**: **raise**. A run that leaves a
  half-wired provider behind is worse than a failed run with a named fix.

Add/remove both belong to the consumer topic: it owns the logic to add the
integration and to take it back out under `--tags remove`. This is the
convention queued in TASKS.md § Now (the opencode/OpenRouter case is the first
application; herdr's agent integrations are the second).

## Recipe: service ownership for daemon-backed topics

A topic that installs a daemon owns the unit that keeps it running — in the
same change as the thing that creates it (spec.md § Layering — teardown
changes with the thing it creates).

- **Darwin**: a per-user launchd agent under `~/Library/LaunchAgents`,
  bootstrapped into the `gui` domain (`launchctl bootout gui/$(id -u)/<label>`
  then `bootstrap` then `enable`), plist from `templates/*.plist.j2`, logs to
  a state dir, health check after boot. Precedent: `apps/ollama`.
- **Debian**: a systemd **user** unit under `~/.config/systemd/user/` — same
  ownership as the launchd agent, no root. It only fires while the user has a
  session, so report the `loginctl enable-linger` fix rather than silently
  changing login behaviour. Precedent: `apps/ollama` user units.
- Point `ExecStart`/`ProgramArguments` at a **stable path** (a shim or a
  resolved-at-install absolute path), not a version-pinned install path that
  changes on every upgrade.
- Teardown: bootout/bootctl disable, remove the unit file, remove logs only if
  they are topic-owned state.

## Recipe: test-first topic program (swarm + measured judge)

The process settled 2026-09-19, instance: herdr. Full methodology for the
judge half lives in `docs/JUDGE-SELECTION.md`.

1. **Queue the task before building** — TASKS.md lines with done-conditions,
   committed immediately; claim any § Cross-session-hazards file.
2. **Write the design down before anyone tests it.** The decisions live in a
   topic README (the instance) and, where they generalize, in this file. A
   swarm can only deduce from written artifacts.
3. **Calibrate the judges before using them** — small injected-defect set
   derived from the topic contract; score catch-rate and false-positive rate;
   never assert judge quality.
4. **Swarm authors the suite before the implementation exists.** Fresh-context
   agents read the written artifacts only (spec, TOPICS.md, task lines,
   README, upstream docs) — never the implementation, never each other — and
   author failing-first suites along four dimensions:
   - **lifecycle contract**: tags, CRUD/teardown invariant, `topic.yml` schema;
   - **catalogue + integration logic**: slice resolution, skip-vs-raise in
     both directions, property tests on pure helpers, fuzzed hand-edited YAML;
   - **user acceptance**: render under both OSes with `StrictUndefined`, the
     flows the author runs;
   - **edge/stress**: malformed catalogue, consumer absent, partial
     integrations, stale service state.
5. **Implement to green**, then prove the tests fail: mutate the mechanism and
   watch the suite go red on the right tests (spec.md § Verification). A guard
   is proven to relent both ways.
6. **Judge rounds**: a single cheap judge mid-rounds, a fusion panel for final
   sign-off, capped rounds, converged when two consecutive rounds surface no
   new high-severity gaps. Dissent is recorded, not averaged away.
7. **Real-machine passes are the author's** — agents never run `chezmoi
   apply`/`run-role.sh`; the suite states honestly what was not exercised.

## See also

- `docs/TOPICS.md` — topic structure, schema, lifecycle (source of truth)
- `home/dotfiles/apps/herdr/README.md` — the instance this file generalizes
- `docs/JUDGE-SELECTION.md` — the measured judge methodology
- `TASKS.md` § Now — the normative topic spec session consumes this file
