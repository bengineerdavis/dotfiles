# Changelog

What changed here, written for someone who wants to know what is different since
they last looked.

This is not `git log`. A commit message serves someone reverting one change and
asking what it was; this serves someone asking what changed and why they should
care. Both are kept, deliberately, because they answer different questions.

Entries are written as fragments in `changelog.d/` at the time of the change and
collected here after each PR merge. Add one with:

```bash
uv run --with scriv scriv create
```

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

<!-- scriv-insert-here -->

## PR #108 — 2026-10-30

**Changed**

- The global mise config is now a regular chezmoi-managed copy rather than a
  symlink into the source checkout. Source changes no longer change the live
  config until you apply them. Local `mise use -g` edits need deliberate capture
  before a later apply; DOT-240 retains that capture-trigger design.

## PR #89 — 2026-10-30

### Changed

- loreai: the opencode extension task now verifies the plugin is installed
  and loading, not merely registered in the deployed config. Measured
  2026-10-27: the config listed `@loreai/opencode` while the shared
  server's in-process auto-install failed for hours (protocol errors,
  then lock-timeout collisions, in the opencode server log), and once
  installed via `opencode plugin add` the loader still rejected 0.40.0's
  pre-v2 function-shaped default export — so a config grep reported a
  working gateway that was not there. The task now reads the structured
  `opencode api get /api/plugin` response and the server log, and names the
  fix per state: manual `plugin add` plus `opencode service restart`, or an
  upstream BYK/loreai release for the load rejection. An active package row
  proves loading; a failed row reports the loader's error. Malformed or
  unavailable API responses cannot be mistaken for a loaded plugin.
- loreai: registered-but-broken opencode plugin states now raise instead of
  whispering in a debug line — a wedged auto-install fails the run (the fix
  is two local commands), and a loader rejection of a pre-v2 plugin export
  raises red without blocking the playbook (`ignore_errors`; recap
  ignored=1). Verified live under `--check`: the loader rejection surfaces
  as FAILED!/ignored=1 while the rest of the topic stays green.

## PR #105 — 2026-10-29

### Fixed

- Repaired the local documentation links found by the new offline Lychee checks.

## PR #104 — 2026-10-29

### Added

- Defined the Lychee link-checking cadence and the security boundary for external URL validation.

## PR #103 — 2026-10-29

changed

- Moved the chezmoi payload, including Ansible and Molecule state, under
  `home/` via `.chezmoiroot`. Repository tooling and project documentation
  stay outside the payload. Existing deployed target paths are unchanged;
  run `chezmoi apply` from main after review.

## Backlog through 2026-10-28

**Added**

- opencode topic (`apps/opencode`): installs the opencode binary from the
  pinned anomalyco/tap on macOS and Linux, and declares the machine's
  cross-agent skill set (five skills, installed user-global via dotagents).
  Homebrew 7 will not load a third-party tap's formulae until the tap is
  trusted, and it reports the refusal as `invalid syntax in tap!` at tap time,
  so the topic runs `brew trust --tap` first; `opencode_remove_tap` now
  revokes that trust alongside the untap.
  Skills auto-load in opencode, claude and cursor from `~/.agents/skills`;
  `--tags remove` uninstalls the binary and keeps the shared skills unless
  `opencode_remove_skills` is flipped.
- chezmoi now manages `~/.config/opencode/opencode.jsonc`: sessions never
  auto-share, one hosted default model with a local small model, and a
  conservative permission baseline (git allowed, everything else asks).
  Provider tokens and session history stay machine-local, as before.

**Added**

- `docs/AGENT-ARTIFACTS.md` — the agent-artifact manager decision:
  skills follow the agentskills.io open format, dotagents installs them
  (pinned refs, committed lock, symlinked canonical store), skills.sh is a
  discovery channel only. Records the survey, the rejected candidates with
  reasons, and the exit path if the manager needs replacing. The queued
  dotagents topic consumes it.

**Changed**

- `docs/REFERENCES.md` gains rows for the Agent Skills spec and dotagents
  (both verified 2026-09-12), updates AGENTS.md's row with its Linux
  Foundation stewardship, and adds a watch list for MCP, ACP, Agent Plugins
  v1 and skills.sh — tracked, deliberately not followed today.

**Added**

- `docs/MODEL-ACCESS.md` — the model-gateway and tool-boundary
  decision, from the author's anti-lock-in brief: the `llm` CLI with provider
  plugins stays as the model layer (it is the only layer the egress policy
  resolver wraps; no surveyed gateway implements that), MCP is the adopted
  tool-execution boundary for when tool exposure is needed (spec 2026-07-28,
  nothing stood up yet), and managed gateways like Vercel AI Gateway are
  rejected for personal use because they move the egress decision off-device.
  LiteLLM is deferred with a named revisit trigger: a second developer
  depending on these workflows. The brief's third vector was already decided
  in `docs/AGENT-ARTIFACTS.md` the same day.

**Changed**

- `docs/REFERENCES.md`: MCP watch-list entry updated to spec 2026-07-28 with
  the record link; LiteLLM added to the watch list (deferred, trigger named);
  Vercel AI Gateway and native vendor SDKs recorded as deliberately not
  followed, with reasons.

**Changed**

- `docs/MODEL-ACCESS.md` — clarified at the top that the decision
  adopts nothing: today's model layer is unchanged (the `llm` CLI), and an
  employer-boundary paragraph states that no decision here licenses anything
  on a work-governed machine. The LiteLLM revisit is now explicitly gated on
  employer permission and on what the MIT core covers versus the enterprise
  tier, since the author flagged company use as an open question.
- `docs/REFERENCES.md` — restored ACP to the watch list (it was dropped when
  the model-access decision rewrote the list) and added A2A
  (a2a-protocol.org, Linux Foundation), both tracked-not-followed.

**Added**

- Agent work-routing policy (`AGENTS.md` § What agents do here): agents in
  this repo work the trunk — which tools, services and configurations belong
  on which machines, with per-machine granularity. Anything needing a build
  follows a three-step ladder: outsource it (AI work to `ai-prompt-library`,
  impromptu eventually), notify and ask, or refuse outright if the author
  declines. Probable builds hidden behind surface-valid config work are
  surfaced to the author for override; determinant detection functions are a
  recorded requirement on the future `topic` CLI / configuration CLI agent
  (`ROADMAP.md`), not something agents build here themselves.

**Added**

- Topic bundles, as a milestone: data-first grouping (`apps/bundles/*.yml`)
  where the bundle config object owns member lists, run order, shared
  configuration, and machine targeting — relationships live in the bundle,
  not inside each topic, so grouping is visible without opening every topic
  and topics stay standalone-installable. Bundle-limited install, update and
  teardown land in the parent playbook first; the `topic` CLI consumes the
  same files after its MVP. First instance is an AI-strategy bundle composed
  per machine. Requirements in `PRD.md` § Bundles compose topics; three work
  items in `TASKS.md` § Topic bundles.

**Added**

- `docs/MULTI-MACHINE.md` — the multi-machine contribution research
  record: the requirement is environment-general committed artifacts (no
  machine identification, no obfuscation signaling) under a forced-disclosure
  threat model, with ZDR handover context kept local by default and
  promotable only after pseudo-anonymization through the pii-redactor tool.
  Contains the audited list of machine-adjacent content already committed,
  a survey of chezmoi/git/Ansible practice, the design (privacy by
  generalization; local state in `~/.local/state/chezmoi/` — a machines map
  and a discardable handover store), and rejected options with reasons
  (including a withdrawn role-codename draft). Four open questions go to a
  panel-of-judges council, queued in ai-prompt-library with a
  questioning-first workflow; implementation waits for that verdict.

**Changed**

- `TASKS.md` queues the machine-string sweep as its own item, gated on the
  council verdict.

**Fixed**

- `cosine()` in `apps/ollama/files/executable_ollama-evals` returned values
  above 1.0 when a norm's square underflowed to subnormal — floating point
  no longer honoured Cauchy-Schwarz there. It now returns 0.0 for norms
  that small, and hypothesis's shrunk counterexample is pinned as its own
  example test beside the property. Found by the 2026-09-11 suite run,
  untracked for three days, fixed and mutation-proven on 2026-09-14
  (6c3079b).

**Changed**

- The `npm:@sentry/skillet` pin moves 1.7.0 → 1.8.0 with verification
  recorded (`skillet validate .` exits 0; the dependency trouble behind the
  earlier rollback did not reproduce). Dropping the pin to `latest` stays
  gated on the upgrade.yaml pin-print, the npx aliases, and the spec.md /
  REFERENCES.md alignment (ee09e38).

**Fixed**

- The dependency check failed for `opencode` — and would fail for any topic
  requiring `homebrew` — on a Debian box running linuxbrew: it probed for a
  `homebrew` binary, but Homebrew's CLI is `brew` on every platform, so the
  check reported `[TOPIC_NOT_RUN]` for a dependency that was present. The
  resolver now maps the `homebrew` token to the `brew` binary
  (`roles/topic-resolution/defaults/main.yaml`), so the requirement resolves
  via the `apps/homebrew` topic on macOS and via linuxbrew on the PATH on
  Debian.

**Changed**

- Dependency resolution moved out of `playbook.yaml` pre_tasks into a shared
  `roles/topic-resolution` role, so it is tested under both OS families rather
  than only observed on whichever machine last provisioned. Behaviour is
  unchanged: the same facts are emitted and the same three states
  (`OK` / `TOPIC_NOT_RUN` / `NO_TOPIC`) are enforced.

**Changed**

- opencode project permissions were reworked (`opencode.json` →
  `opencode.jsonc`): rules deduplicated and reordered so last-match-wins falls
  the right way, interpreters and the test/lint toolchain are now `allow`,
  `chezmoi apply` is denied, and an opt-in `autonomous` agent widens the
  frequent-but-reversible operations (commit/push, `gh`, fetches, installs,
  model pulls, webfetch) without touching the deny tier.
- The global opencode template's bash catch-all moved first — it had sat last,
  which would have turned every command into a prompt at the next restart.
- History rewriting (`git filter-repo`/`filter-branch`) changed from `deny` to
  `ask` in both opencode and Claude Code, so the human sees the command and
  applies the backup-branch + `git notes` ceremony per invocation. Force-push
  stays denied.

**Security**

- The Claude Code config's secret-path deny rules named a different machine's
  macOS home (`/Users/ben.davis/...`), so on this machine they never matched
  and the secrets they guarded were reachable in principle. They now use `~`
  and apply on any machine.

**Added**

- `docs/LANGUAGES.md` — which languages the repo's scripts use, and the
  reusable per-language tool profile.

**Added**

- The `herdr` topic (`dotfiles/apps/herdr`): installs the agent-runtime server
  through mise with the topic owning the entry (`mise use -g herdr` /
  `mise unuse --global herdr`, probe-first, capture committed), wires agent
  integrations from a new shared catalogue (`dotfiles/config/agents.yaml` —
  opencode and claude wired, cursor skip-and-report, all 18 upstream ids
  accounted), owns the server as a launchd gui-domain agent (Darwin) and a
  systemd user unit (Debian) at the stable mise shim path, captures a minimal
  `~/.config/herdr/config.toml`, and generates a topic-owned zsh completion
  into `~/.zfunc/_herdr`. Teardown is gated (`herdr_remove_integrations`,
  default off) and intersection-only, ordered integrations → service → entry.
- A test-first swarm-built suite (`tests/herdr/`, 108 tests): four independent
  fresh-context authors deduced the contract from written artifacts before the
  topic existed, plus an executable contract module the YAML is pinned against.
  A measured judge loop (see `docs/JUDGE-SELECTION.md` and
  `tests/herdr/calibration/`) ran one ITERATE round and a unanimous SHIP panel.
- Two reusable docs from the same work: `docs/TOPIC-RECIPES.md`
  (install-mechanism chooser, catalogue pattern, skip-vs-raise, service
  ownership, the test-first recipe) and `docs/JUDGE-SELECTION.md`
  (the calibrated judge methodology, with the measured pool recommendation).

**Fixed**

- The remove-side status parsing was written against an assumed JSON wire
  shape; measured on the real binary (herdr 0.9.1) the format is
  `<id>: installed|not installed (<path>)` lines — including a
  `(experimental)` annotation variant — and the YAML grammar regexes carried
  a latent double-escaping bug (never would have matched). Both corrected
  against the binary; a golden-transcript test now pins the real wire.

**Changed**

- `apps/mise/files/config.toml` gains the `herdr = "latest"` entry with the
  ownership comment — the capture the topic's first-party commands write
  through the deployed symlink.
- Real machine state is **not** touched: converge, second-run idempotence and
  remove are the author's three passes; the `mise upgrade` output predicate
  and `launchctl enable` idempotence are recorded as what that pass settles.

**Added**

- A `deep` opencode agent that opens on Claude Opus 5 (via OpenRouter) at max
  reasoning effort, with `xhigh`/`medium` variants to cycle down to. The
  default model is unchanged.
- opencode model, provider and agent settings now live in
  `.chezmoidata/opencode.yaml`, layered `common` → `os.<darwin|linux>` →
  `hosts.<hostname>`. Share a setting across machines by moving it to
  `common`; give one machine its own by adding a `hosts` entry. Permissions
  stay literal in the template because their order matters. Project configs
  stay in each project's own git.

**Fixed**

- The ollama server is restarted when an upgrade leaves it running the old
  binary. Until now, `brew upgrade` replaced the binary and
  `com.ollama.server` went on running the previous version until someone
  restarted it by hand. The new shared role `roles/restart-stale` restarts a
  service or app only if its process started before the binary's ctime.
  `apps/ollama` is its first caller.

**Changed**

- The `1password` topic now also manages the 1Password desktop app on macOS,
  as the `1password` Homebrew cask. The existing app in `/Applications` is
  adopted in place, not moved or copied. The app stays in `/Applications`
  rather than `~/Applications` because 1Password's browser integration requires
  it. 1Password's own updater still does the updating. If an update leaves the
  old app running, the next install or upgrade run quits it gracefully and
  reopens it. If the app does not quit, the run reports it and leaves it
  running.

**Fixed**

- Automatic GUI restarts now quit and reopen the same app bundle, even when
  another copy has the same name.
- A failed process probe stops the restart check. It is no longer treated as
  evidence that the app stopped, which could reopen it and report success.

**Added**

- `skill-trust` recognises a foreign skill bucket — another program's directory
  in the skills store, like Claude Code's `synced/` — as `external` rather than
  denying it. Detection is by evidence (the path, a `.bucket-<id>` marker, and a
  `manifest.json` with a `skills[]` array), and a `deny` on such a bucket is
  refused with the reason rather than attempted. `foreign_buckets: false`
  restores the old fail-closed denial.

**Fixed**

- Provisioning no longer fails outright when Claude Code's cloud-synced skills
  are present: the approved-sources guard now recognises that bucket as out of
  its jurisdiction, and runs as the last task in `apps/opencode` so one
  offending skill cannot block the rest of the install.

**Added**

- A molecule + Vagrant topic-test harness: `scripts/run-molecule.sh <topic>
  [verb]` drives per-topic molecule scenarios from anywhere, through the new
  locked `test-vm` uv dependency group (molecule 26.9.0,
  molecule-plugins[vagrant] 26.9.28, pytest-testinfra 10.2.2,
  ansible-core 2.21.5) with `community.vagrant` 1.0.1 pinned in
  `dotfiles/requirements.yml`. First scenario: `apps/opencode` — vagrant
  boots `debian/bookworm64` under libvirt/KVM, prepare bootstraps the box to
  the pre-migration state (apt, linuxbrew, mise+node, chezmoi, the v1
  formula), converge imports the topic role, and pytest-testinfra asserts the
  v2 migration's end state (v2 formula installed, v1 gone, `opencode
  --version` 2.x, the migrated config loads with its ordered permissions
  array, skills synced, tap trusted). Scenarios live inside the topic at
  `apps/<topic>/molecule/default/` per the recorded molecule-adoption
  conventions; a `test-vm` run provisions a VM one box at a time and never
  touches the host beyond the user-level ansible collections directory.

**Changed**

- The global opencode `external_directory` boundary now also allows the two
  external-skill trees, `$HOME/.agents/skills/*` and `$HOME/.claude/skills/*`.
  Motivating case: `aboyeur`, installed 2026-10-13, was unreadable from a
  session started earlier — opencode's runtime auto-allow only covers skill
  directories registered at session start, so mid-session installs and
  unregistered directories had no rule. The static allows make the trees
  readable in every session without per-skill entries. Contract test updated
  (trio → deny + four allows), mutation-proven; the boundary stays
  deny-everywhere-else.

**Added**

- `apps/dotagents`: a new topic that owns the machine's global agent-artifact
  declaration — the approved source list, the source-trust allow-list, the
  per-source excludes, the vendored-skill exceptions, and the sync that
  installs them. It calls the mise-pinned `dotagents` binary rather than
  `npx @sentry/dotagents@latest`, so one version exists on the machine.

**Changed**

- The global skill declaration moved out of `apps/opencode`. That topic keeps
  the binary and config and no longer carries a skill manifest, and `node` is
  no longer one of its dependencies.
- The provenance guard runs from `apps/dotagents`, still last in the install,
  and receives that topic's source and vendored lists.

**Known issues**

- `dotagents init --force` deletes the skills store (measured 2026-10-26), so
  init runs only when `agents.toml` is absent. Changing the agent list later is
  a deliberate destructive act.
- A fresh `init` installs a `dotagents` skill from an untrusted source; install
  removes it immediately so the provenance guard does not fail on it.

**Added**

- `mattpocock/skills` is an approved skill source. MIT, verified 2026-10-26
  with `gh api repos/mattpocock/skills`. It is a plugin-marketplace repository,
  so dotagents installs it as a plugin rather than a wildcard skill source.

**Known issues**

- A plugin source's skills are linked into `~/.config/opencode/skills` only.
  dotagents publishes client marketplaces under `~/.agents/` but does not point
  claude, cursor, codex or copilot at them; per-client wiring is queued as its
  own task.
- Plugin skills sit outside the provenance audit, which reads
  `~/.agents/skills`. A plugin source is approved by source trust alone.

**Added**

- `docs/agents/` configures the Matt Pocock engineering skills for this repo.
  The issue tracker is `backlog-md-py` (`backlog-py` CLI, `backlog-py-mcp`
  server), with `TASKS.md` named as the interim queue until the cutover. Triage
  uses the five canonical labels. Domain docs are `docs/GLOSSARY.md`; ADRs are
  created with `backlog-py decision create` under `backlog/decisions/`.
- The `backlog-py-mcp` server is registered for opencode under `mcp.servers` in
  `.chezmoidata/opencode.yaml`, ahead of the cutover.
- `docs/BACKLOG-UPSTREAM-CONFIG.md` records that neither Backlog.md nor
  backlog-md-py can point docs or decisions outside the backlog folder, with
  the drafted upstream PRs to change that.

**Known issues**

- The MCP server starts and answers `initialize` with no `backlog/` project
  (verified 2026-10-26), but its task tools have nothing to act on until the
  cutover. Registration is deliberate so the surface exists when the queue
  lands; calls fail until then.
- `backlog-py` exposes no decision tools over MCP. ADRs are a CLI verb until
  the upstream work in `docs/BACKLOG-UPSTREAM-CONFIG.md` lands.

**Changed**

- The agent temp root is allowed outside the project: `~/.cache/tmp` for
  handoff documents and scratch files. `/tmp` is not allowed; the access that
  once needed it came from running mise under sudo, which the shell and
  Ansible guards refuse.
- `npm:@sentry/dotagents` is pinned to `3.3.0` rather than `latest`, so the
  binary the dotagents topic calls is the one the machine has. `latest` left
  the pin implicit and let 3.4.0 arrive through a separate `npx` channel.
- `github:danielmiessler/fabric` is bumped to `1.4.516` while upstream's
  version-prefix handling is checked. The duplicate-tree failure in the comment
  was measured at `1.4.478`.

**Added**

- `roles/guards/no-root-authority.yaml` refuses a run that would install a
  user-scoped tool as root. A whole play started through sudo cannot be
  corrected by `become: false`: that means "do not elevate", not "refuse to run
  as root". `apps/mise` calls it with `always`, and the tests prove it fires for
  root and relents for a normal user.
- `dot_functions` gains a `sudo` wrapper that refuses `mise`, `ansible` and
  `ansible-playbook` while passing every other command through. `command sudo`
  still bypasses it on purpose.
- The global opencode permissions, and the repo project config, deny `sudo`
  for agents.

**Changed**

- The mise commands carry explicit `become: false`, so a play-level `become`
  cannot elevate them even if the guard is bypassed.

**Known issues**

- `sudo -i` opens a root shell, and neither the wrapper nor Ansible can inspect
  what runs inside it. That is deliberate root work rather than an accidental
  `sudo mise`.

**Fixed**

- `.chezmoiignore` now covers the repo tooling added after its per-file docs
  list was written: `backlog/` (the task queue) and `docs/agents/`,
  `docs/BACKLOG-MIGRATION.md`, `docs/BACKLOG-UPSTREAM-CONFIG.md`. Without this,
  `chezmoi apply` would create `~/backlog` and deploy repository documentation
  into `~/docs`.

**Changed**

- `chezmoi apply` moves from `deny` to `ask` for agents. The convention changed
  with the configuration: an agent may apply only from `main`, after showing
  `chezmoi status` and `chezmoi diff`, and the prompt is the author's approval.
  The `autonomous` agent asks too; applying touches the one deployed tree.
- `AGENTS.md` § Applying is main-only and `docs/PERMISSIONS.md` record the new
  rule, including what to do when a target changed since chezmoi last wrote it.

### Added

- pii-redactor's deterministic pass now redacts iOS crash-report identifiers
  (device/vendor UUID fields, per-install container paths, uid, A/B-trial ids),
  HAR cookie and authorization values in both header and JSON forms, Sentry
  DSNs, and local paths. Paths collapse to a typed placeholder that keeps the
  code-identifying leaf — `/Users/jane/x/App.app/App` becomes
  `[HOME]/App.app/App` — so a reader still knows what crashed, never where it
  lived.

- Root `pyproject.toml` and `uv.lock`: the test suite now runs from locked
  dependency groups instead of a seven-flag `--with` incantation. `uv run
  --frozen` rebuilds the environment offline from cache. The repo is never
  built or installed (`package = false`).

- roborev topic (`apps/roborev`): the automatic AI code-review daemon, on
  both machines. macOS installs the `roborev` formula from upstream's
  `kenn-io/tap` tap, trusted before tapping — Homebrew 7 refuses an
  untrusted third-party tap at tap time and the refusal names neither cause
  nor fix. Debian fetches the release `.deb`, checksum-verified against the
  GitHub API's per-asset digest, and owns its own upgrades because
  `apt upgrade` cannot reach a GitHub-release deb. `--tags remove`
  uninstalls the binary and keeps the tap unless `roborev_remove_tap` is
  flipped, mirroring `apps/opencode`.

- opencode topic: declared the ten roborev-bundled skills as vendored in
  `opencode_skill_vendored`, each directory carrying LICENSE and PROVENANCE.md.
  `roborev skills install` writes them into ~/.agents/skills (and
  ~/.claude/skills), but roborev's skills are not a git source dotagents could
  reference, and MIT licence + the vendored declaration is what the
  approved-sources guard audits against. Refresh is deliberate: a roborev
  upgrade rewrites those directories and may drop PROVENANCE.md — the guard
  fails loudly when it does, by design.
- Also on 2026-10-15: retired the stray mise/npm opencode installs (1.18.30,
  1.18.32 — no config ever declared them; `mise ls` "not active" residue of the
  pre-v2 era), so `opencode` resolves only to the brew opencode-v2 binary, and
  installed `skill-trust` via uv tool (the approved-sources guard names it as
  its own fix and it was absent).

- `~/.zshenv` (chezmoi): TMPDIR defaults to `~/.cache/tmp` when unset and
  usable, exported only after the directory is created and verified writable
  (an unusable dir falls back to stock /tmp). Reason: aube derives its npm
  lock dir from TMPDIR and defaults to shared `/tmp/fslock`, which a root run
  had created root-owned — breaking npm installs for every user on a machine
  whose /tmp never self-clears. Accumulation handled by the new user
  tmpfiles rule (`~/.config/user-tmpfiles.d/tmp.conf`, 30-day purge).
  Known bounds recorded in the file: cron's /bin/sh bypasses zsh, and
  preserved-env privileged runs are out of reach of shell config.

- `~/.config/user-tmpfiles.d/tmp.conf`: age `/tmp/opencode` (opencode's
  agent scratch dir) on the same 30-day schedule as `~/.cache/tmp`.
  The dir accumulates unbounded — 35+ stale entries spanning weeks were
  observed on 2026-10-17 — because `/tmp` never self-clears on
  root-fs machines and no tool cleans it. The `e` type cleans contents
  of the existing dir only; live sessions are unaffected, and the
  already-running `systemd-tmpfiles-clean.timer` does the sweeping.

- `topical new` — manager-aware topic scaffolding, living in its own repo
  at `~/code/personal/topical`. Scaffolding a topic now fills `topic.yml`
  from flags and emits only the install/remove blocks the declared package
  managers need, reading this repo's `dotfiles/managers.yaml` — instead of
  copying a five-way commented menu and leaving every field to
  hand-editing. `apps/firefox` was regenerated with it and is
  byte-identical to the generator's output.

- loreai topic (`apps/loreai`): the Lore.AI persistent-memory gateway for
  coding agents. The `lore` binary installs checksum-verified from
  BYK/loreai releases (the `apps/ori` pattern — the topic owns its
  upgrades), first-install prompts for telemetry and worker-model
  inference are saved per machine to `~/.config/loreai/env.zsh`, and each
  detected coding agent is wired up as an extension: `lore setup` for
  claude-code/codex/pi/hermes, and a chezmoi-included
  `@loreai/opencode` plugin fragment for opencode, whose config chezmoi
  owns. Background workers default to OpenRouter (`z-ai/glm-5.3-flash`)
  where a key is available, with reviewed fallbacks and a 32B-class local
  tier recorded in the machine env file. `--tags remove` undoes each
  agent's setup and removes the binary while preserving the memory
  database.

### Changed

- The topic conventions document is now named for what it contains:
  `docs/TOPICS.md`, not `CONVENTIONS.md`. Every reference across 56
  files moved with it, including the three in `template_dir/` that every newly
  scaffolded topic inherits.

- mise: `@sentry/skillet` approved past aube's npm supply-chain threshold
  (`allow_low_downloads = true`) — aube had refused it at 7 weekly downloads
  against the 1,000 threshold; the approval is recorded in-tree next to the
  tool entry with the verification note. roborev is intentionally NOT pinned
  in mise: `apps/roborev` remains the sole install owner (checksum-verified
  .deb on Debian, brew on Darwin), and a mise shim would shadow the
  topic-installed binary.

### Removed

- `dotfiles/template_dir` and `init-config.sh` — the canonical topic
  skeleton moved to the topical repo, and `topical new` replaces the
  verbatim-copy scaffolder. The next `chezmoi apply` removes both from
  `~/dotfiles`.
- Twenty dead topic-root files nothing loaded: twelve `tasks.yaml` with
  unedited template boilerplate, three whose install task duplicated the
  lifecycle install, and five `main.yaml` leftovers.

### Fixed

- Repo tooling no longer deploys to `$HOME`: convention docs (`LANGUAGES.md`,
  `GLOSSARY.md`, `WORKTREES.md`), hook scripts (`scripts/`), `tools/`, and
  two stray `bin/` backups are ignored. The governance guard now works from
  git worktrees (`chezmoi -S`) and covers project files.

### Breaking changes

- **The task queue is now `backlog/` (backlog-md-py); `TASKS.md` is
  deleted.** This breaks every in-flight branch that touches the old
  files: rebase onto main and convert — `docs/BACKLOG-CUTOVER.md` is the
  procedure (cutover wins; import branch-added items, take the
  deletions). All 177 queued items were imported as per-task Markdown
  files, validated on a repo copy first; the old files' final state is
  pinned at the `archive/tasks-md` tag. Agents manage the queue through
  the `backlog-py` CLI or the `backlog-py-mcp` MCP server (registered
  for opencode). Claims are orchestration leases with expiry and version
  checks instead of lines in § Claimed, and `backlog/` writes commit
  straight to main as coordination overhead — the one carve-out to
  everything-is-branched (author ruling 2026-10-23). The `apps/backlog`
  topic owns the pipx install and the singleton daemon's per-user
  service unit; worktrunk is installed alongside for worktree mechanics.
  Decision record: `docs/BACKLOG-MIGRATION.md`.

<a id='changelog-Unreleased'></a>
## Unreleased — 2026-09-10

### Added

- A changelog. Entries are written as fragments in `changelog.d/` when the
  change is made and collected here on release, so nothing is reconstructed
  from commit messages later.
- Contribution standards for agents and people in `CONTRIBUTING.md`,
  including what to do when an agent fails part-way through a task.
- A register of every external standard this repo follows, in
  `docs/REFERENCES.md`, with the version followed and when it was last checked.

### Changed

- Agent permissions were rebuilt from scratch. Publishing, installing and
  deleting ask first. See the backlog entry dated 2026-10-28 for the later
  main-only `chezmoi apply` approval rule.

### Fixed

- The git hooks had never run. `.pre-commit-config.yaml` was configured but no
  hooks were installed, so shellcheck had never checked anything.
- The documented test command was missing a dependency and produced 53 errors
  when run exactly as written.
