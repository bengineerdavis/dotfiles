# opencode — changelog

Section names come from antsibull-changelog; see `docs/TOPICS.md`
§ "Per-topic changelog and local edge cases".

## 2026-10-26

### major_changes

- The topic no longer declares or syncs the machine's skill set. The approved
  sources, trust allow-list, excludes, vendored exceptions and the dotagents
  sync moved to `apps/dotagents`; the artifacts are user-global and belong to
  no single coding tool's topic. `node` is no longer a dependency of this topic
  because nothing here runs `npx` any more.

### known_issues

- **Installing this topic alone does not install or refresh skills.** A run
  that converged opencode before this change used to leave the skill set
  current; it no longer does. Run `./run-role.sh dotagents` (or the parent
  playbook) after, or provision both.

## 2026-10-21

### major_changes

- **Unexpected skills are now asked about, not just failed on.** The
  dotagents-approved-sources guard still fails closed, but the run no longer
  dead-ends there: `update.sh` probes the store before the play and, on a
  first detection with a terminal attached, opens `skill-trust resolve` —
  approve, vendor or deny each finding once, with a recorded why, and the
  decision persists in `~/.config/skill-trust/trust.yaml` (machine-local,
  never versioned; deny outranks approve across the layers). A recorded
  rejection keeps failing until the thing is actually removed. The guard's
  failure message now names both that resolver and the non-interactive
  `skill-trust trust add`, alongside the one-run
  `-e guard_allow_unapproved_skills=true` escape.
  (roborev review #10 on the branch caught the pre-flight piping the
  inventory into resolve's stdin — taking the terminal with it — and a bare
  resolve judging without the inventory; both fixed before merge: the
  inventory travels as a file, and resolve fetches it itself by default.)
- **Hidden directories no longer fail the audit.** Dot-dirs (`.trash` is the
  one that fired) are skipped as non-load-paths and *reported* every run;
  `include_hidden` in the topic's guard vars or the trust store re-audits a
  named directory. Loader verification (dotagents, opencode, codex verified
  to skip dot-dirs; claude-code, cursor, copilot unverified) is recorded in
  `tools/skill-trust/README.md`.
## 2026-10-19

### known_issues

- **A second install channel appeared outside the topic and shadowed the
  brew route.** Measured 2026-10-19 on the drift box: `which opencode`
  resolved to the mise shim, serving an `http:opencode@2.0.32` install
  (mise's direct-URL backend) rather than the brew binary this topic
  installs. The versions coincided at 2.0.32, so the shadowing showed
  only in `which`, not in output — the channel, not the version, was the
  drift. The entry is not in the repo's mise config and never was:
  `git log -S "http:opencode"` over all history finds no config commit,
  and in `mise ls --json` the entry carries no `source` key while owned
  tools (e.g. `herdr`) carry one pointing at the config that declares
  them; `mise which opencode` reports it "not currently active". The old
  `opencode@1.18.32` (aqua backend) sits beside it, equally unowned. This
  is the same failure shape as the roborev incident recorded in
  AGENTS.md § Cross-repo changes: an install made without declaring it,
  outside the tool-entry-ownership recipe (docs/TOPIC-RECIPES.md),
  shadowing the topic's route.
  The leftovers live in `~/.local/share/mise/installs/http-opencode/` and
  `~/.local/share/mise/installs/opencode/`, plus the stale shim at
  `~/.local/share/mise/shims/opencode`. Removal is author-run (mise
  machine state, not topic or repo state):

      mise uninstall "http:opencode@2.0.32"
      mise uninstall "opencode@1.18.32"
      mise reshim
      type -a opencode   # expect only the linuxbrew path left

  The canonical route is unchanged: brew, `anomalyco/tap/opencode-v2`,
  installed by this topic's `install.yaml`. No topic change was needed
  for the two-version v1 state the same day's audit asked about
  (1.18.32 and 1.19.3 under one formula name): `state: absent` runs
  `brew uninstall --force` (community.general 13.0.1,
  `_uninstall_packages`), and this box's own Homebrew 7.0.9 documents
  `--force` as "Delete all installed versions of formula" — one task
  converges any number of installed v1 versions.

## 2026-10-06

### breaking_changes

- The topic now installs opencode v2 (`anomalyco/tap/opencode-v2`) and removes
  the v1 binary in the same run: the v2 formula declares `conflicts_with
  "opencode"`, so brew refuses the v2 install while v1 is present.
  `install.yaml` uninstalls `anomalyco/tap/opencode` first and cleans its
  formula trust residue (`brew untrust --formula`) — idempotent, a no-op
  where v1 never ran.
- Config keys migrated to the v2 schema in
  `dot_config/opencode/opencode.jsonc`: the v1 `permission` map becomes the
  ordered `permissions` array (`bash` rules renamed `shell`; v1's `list`
  rule dropped — not a v2 action; the trailing shell catch-all dropped —
  author ruling 1), and `autoupdate` becomes `update: notify`. v2 still
  parses the v1 map through its legacy layer, but the topic ships the
  native form (docs/research/opencode-v2/PLAN.md).
- Re-auth is likely: v2 stores credentials in a sqlite `credential` table,
  and no import of v1's `auth.json` was found in the v2.0.24 source.
  Sessions migrate in place on the first v2 run; back up
  `~/.local/share/opencode/` before it (see `known_issues`).

### minor_changes

- The binary installs from `anomalyco/tap/opencode-v2` on the same pinned tap
  (`opencode_tap` unchanged). Upgrade doctrine unchanged: the binary is still
  a brew formula, so the homebrew system role's `upgrade_all` keeps it
  current and `upgrade.yaml` stays a stub.
- Trivial-model roles stay local: `small_model` and v2's `agents.summary.model`
  / `agents.compaction.model` pin `ollama/qwen3.5:9b` (author ruling 3), so
  titles, summaries and compaction never leave the box.
- The `external_directory` rules carry literal `$HOME/...` globs — v2 expands
  `$HOME` itself at config load, so the home directory is no longer templated.

### known_issues

- **No `auth.json` import path was found in v2.** `credential.ts`,
  `integration.ts`, the v1-migration module and the `auth import` handler
  (v2.0.24 source, checked 2026-10-06) never read v1's `auth.json`; `auth
  import` consumes `auth export` JSON instead. Treat re-auth as required
  until proven otherwise on the box. `auth.json` itself is untouched by the
  v2 code paths, so tokens survive for a v1 rollback.
- **The session migration is in place, not additive.** v2 transforms v1's
  sessions inside the same database on first run; a migrated database may
  not be readable by v1 1.18 again. Back up `~/.local/share/opencode/`
  before the first v2 launch. Sessions created after the migration exist
  only in v2 — that loss is bounded and accepted.
- **The bash allow-list comes back in force, deliberately.** v1's map carried
  a trailing `"*": "ask"` that, by last-match, shadowed every allow in the
  map — the exact state the template's own 2026-09-16 comment describes. The
  migrated array drops the duplicate (author ruling 1, 2026-10-06): after
  migration `git`, `find`, `cat` and the rest of the allow-list run without
  asking, where on a clean v1 restart every shell command asked. The
  behavior change vs the deployed v1 config is accepted; the specific rules
  re-assert the 2026-09-16 intent.

## 2026-09-14

### bugfixes

- Trust `anomalyco/tap` before tapping it. Homebrew 7 refuses to load a
  third-party tap's formulae until the tap is trusted, so the install had been
  failing on macOS and the binary was never present. See `known_issues` below
  for what the failure actually looks like.
- Teardown now revokes both trust entries. `brew trust --tap` writes a tap
  entry and `brew install` writes a separate formula entry; `brew untrust --tap`
  removes only the first, so `opencode_remove_tap` left the formula entry behind.

### known_issues

- **A tap that is not trusted fails at tap time, and the error names neither
  trust nor the fix.** On Homebrew 7.0.1, `brew tap anomalyco/tap` validates
  every formula in the tap, refuses each one as untrusted, and aborts with:

      Error: Cannot tap anomalyco/tap: invalid syntax in tap!

  Nothing in that message mentions trust. The fix is `brew trust --tap
  anomalyco/tap`, which `tasks/install.yaml` now runs first — trust is keyed by
  name rather than by tap contents, so trusting an untapped tap is valid, and it
  is the only ordering that works.

- **`./update` will not install a missing binary.** `update.sh` runs
  `--tags upgrade`, and the binary tasks are tagged `install`/`provision` only,
  so an upgrade pass leaves an absent opencode absent. This is
  the tier model working as designed — `brew upgrade` refreshes what is
  installed — but it means a machine that has only ever run `./update` never
  gets the topic. Use `./run-role.sh opencode install` or `--tags provision`.
  The skill sync is no longer part of this topic's upgrade path either; see
  `apps/dotagents`.

- **The tap tracks releases; homebrew/core trails it.** Measured 2026-09-14:
  tap 1.18.31, core 1.18.30. core's formula sets `livecheck { throttle 5 }`, so
  it follows every fifth release by design. The tap is pinned deliberately for
  that reason — see `tasks/install.yaml`.

- **`opencode auth login` is not automated and will not be.** Tokens live in
  machine-local `auth.json`; a provisioning run does not capture credentials
  interactively. A fresh machine needs it run by hand once.

### minor_changes

- Permission rules now template the home directory. `external_directory` had
  carried literal `/home/bdavis` paths, which never matched on any machine whose
  home was elsewhere — leaving the surrounding `"*": "deny"` as the only rule in
  force, silently. The file is `dot_config/opencode/opencode.jsonc.tmpl` in the
  chezmoi source and renders `{{ .chezmoi.homeDir }}` per machine.
