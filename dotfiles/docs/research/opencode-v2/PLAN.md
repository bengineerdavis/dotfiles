# opencode v2 migration plan (apps/opencode, chezmoi config)

**Checked 2026-10-06.** Feeds the three queued work items in `TASKS.md` § Now:
plan (this document), tests (`orch_sub_oc2test`), implement (`orch_sub_oc2mig`).

Sources checked: opencode.ai v2 docs (`/v2/docs`, `/v2/docs/config`,
`/v2/docs/permissions`), the published schema at `opencode.ai/config.json`, the
v2.0.24 source tree at github.com/anomalyco/opencode (config normalizer, v1
config schemas, migration module, credential/integration layer, CLI command
surface), the tap formula `anomalyco/homebrew-tap` `opencode-v2.rb`, and this
repo's topic files and tests. Every claim below says where it came from.
Section "Not verified" at the end names the gaps.

## Decisions already made (author — recorded, not relitigated)

- Install route: brew tap formula `anomalyco/tap/opencode-v2`. Not npm — npm is
  blocked on this box by a root-owned `/tmp/fslock` (standing machine issue,
  `TASKS.md` § Cross-session hazards).
- The v2 formula declares `conflicts_with "opencode"`, so the topic's install
  removes the v1 formula in the same run, before installing v2.
- Scope includes migrating `dot_config/opencode/opencode.jsonc.tmpl` to the v2
  schema.
- After the ansible migration is verified, the author removes the mise-installed
  opencode 1.18 shadow (it outranks the brew binary on PATH). Author-run machine
  state; the exact commands are in the follow-up section.

## Headline answers

1. **v2 parses v1's `permission` map and migrates it.** The v2 config
   normalizer (`packages/core/src/config/normalize.ts` at tag v2.0.24,
   `migratePermissions`) converts the v1 map into the v2 `permissions` array,
   preserving key order, and `normalizeAction` renames `bash`→`shell`,
   `task`→`subagent`, `write`/`patch`→`edit`. The v1 keys `autoupdate`,
   `agent`, `provider`, `small_model`, `command`, `mode` also migrate. So a
   v1-shaped config still loads in v2 — but this topic migrates its config to
   native v2 keys anyway (author decision), because the native form is the
   documented contract and the legacy layer is upstream's compat path.
2. **v2's `permissions` is an ordered array; matching is LAST-match-wins** —
   the same semantics the v1 map relied on (`/v2/docs/permissions`: "The last
   matching rule wins"; the default base policy is listed first and global
   rules are "appended next"). Translation is therefore order-preserving: the
   JSON key order of each v1 sub-map becomes the array order, unchanged. The
   one semantic gap: the current template's bash map carries a trailing
   `"*": "ask"` (line 69) that, by last-match, shadows every allow in that map
   — the exact state the file's own comment says was fixed on 2026-09-16. The
   migration expresses the documented intent and drops the duplicate
   (open decision 1).
3. **Sessions migrate automatically; auth does not (as far as the source
   shows).** v2 opens the same XDG data tree and transforms v1's `session` /
   `message` / `part` rows in place into `session_v2`, tracked under the KV
   key `migration.v1-v2` (`packages/core/src/database/v1-migration.bun.ts`).
   v2 stores credentials in a sqlite `credential` table, not `auth.json`
   (`packages/core/src/credential.ts`); none of the code I read imports v1's
   `auth.json` — plan for a re-auth, verified on the day.
4. **Brew: uninstall v1, then install v2, in one run.** `conflicts_with` makes
   brew refuse `opencode-v2` while any `opencode` formula is installed; the
   `community.general.homebrew` module with `state: absent` is the idempotent
   way to clear it. Tap and tap-trust tasks are unchanged (same tap); the
   formula trust entry name changes to `opencode-v2`.
5. **Upgrade doctrine unchanged.** The binary is still a brew formula, so
   currency still belongs to the homebrew system role (`upgrade_all: true`,
   `apps/homebrew/tasks/upgrade.yaml`) — `upgrade.yaml` stays a no-op stub and
   the skill-sync tasks keep their `upgrade` tag.

## The exact v1 → v2 permission mapping

Replace the whole `"permission": { ... }` block in
`dot_config/opencode/opencode.jsonc.tmpl` with this `"permissions"` array.
Order within each action group is load-bearing; order across groups is not
(each action is checked against its own rules). Evidence for every rule:
`/v2/docs/permissions` (fields, effects, matcher, last-match, `$HOME`
expansion, actions table) and `migratePermissions` (order preservation,
`normalizeAction`).

```jsonc
"permissions": [
  // Catch-all FIRST: v2 takes the LAST matching rule, so specific rules follow.
  // Same discipline as the v1 map, one syntax later.
  { "action": "shell", "resource": "*", "effect": "ask" },
  // Read-only inspection and text transforms are free. Deliberately NOT
  // allowed (docs/PERMISSIONS.md tiers): xargs (executes piped input the
  // external_directory scan cannot see) and gita's mutating subcommands —
  // both fall through to the catch-all and ask.
  { "action": "shell", "resource": "git *", "effect": "allow" },
  { "action": "shell", "resource": "mise *", "effect": "allow" },
  { "action": "shell", "resource": "cat *", "effect": "allow" },
  { "action": "shell", "resource": "head *", "effect": "allow" },
  { "action": "shell", "resource": "wc *", "effect": "allow" },
  { "action": "shell", "resource": "sort *", "effect": "allow" },
  { "action": "shell", "resource": "comm *", "effect": "allow" },
  { "action": "shell", "resource": "uniq *", "effect": "allow" },
  { "action": "shell", "resource": "echo *", "effect": "allow" },
  { "action": "shell", "resource": "printf *", "effect": "allow" },
  { "action": "shell", "resource": "grep *", "effect": "allow" },
  { "action": "shell", "resource": "gita ls*", "effect": "allow" },
  { "action": "shell", "resource": "gita status*", "effect": "allow" },
  { "action": "shell", "resource": "find *", "effect": "allow" },
  // Carve-outs sit AFTER `find *` so last-match denies them.
  { "action": "shell", "resource": "find *-delete*", "effect": "deny" },
  { "action": "shell", "resource": "find *-exec*", "effect": "deny" },
  { "action": "shell", "resource": "find *-execdir*", "effect": "deny" },
  // Baseline safety: reads and edits are free, network asks.
  // (v2's built-in base policy also asks before reading *.env; the global
  // read-allow below is appended after the base policy and overrides it.
  // Keeping v1 parity — reads free — is open decision 3.)
  { "action": "read", "resource": "*", "effect": "allow" },
  { "action": "glob", "resource": "*", "effect": "allow" },
  { "action": "grep", "resource": "*", "effect": "allow" },
  { "action": "edit", "resource": "*", "effect": "allow" },
  { "action": "webfetch", "resource": "*", "effect": "ask" },
  { "action": "websearch", "resource": "*", "effect": "ask" },
  // Deny FIRST, allows LAST — broad-first, narrow-last, same order as v1.
  // $HOME is expanded by v2 itself when the config loads, so these are plain
  // literals, not chezmoi templates (AGENTS.md rule 1: resolve at the
  // consuming tool where it expands paths itself). `/*` is the docs-canonical
  // boundary form; `*` spans `/`, so one star covers subdirectories.
  { "action": "external_directory", "resource": "*", "effect": "deny" },
  { "action": "external_directory", "resource": "$HOME/.local/share/chezmoi/*", "effect": "allow" },
  { "action": "external_directory", "resource": "$HOME/code/*", "effect": "allow" }
]
```

Mapping notes:

- `bash` → `shell` (`normalizeAction`); v1's `"bash": {"*": "ask", ...}` map
  entries become `{action: "shell", resource, effect}` in the same order. The
  trailing duplicate `"*": "ask"` from v1 line 69 is dropped — see open
  decision 1. Behavior note for review: today, on a clean restart, v1's
  last-match makes every bash command ask; after migration the allow-list is
  in force as the 2026-09-16 comment intends.
- `read`/`glob`/`grep`/`edit` keep their names and become `resource: "*"` rules
  (v1 string values are exactly `{action, "*", effect}` in
  `migratePermissions`).
- `webfetch`/`websearch` keep their names; resource is the URL / query, `*`
  matches all.
- `external_directory` keeps its deny-first/allow-last order. The matcher
  pattern is the same whole-value glob (`*` = zero or more chars including
  `/`), so v1's `~/.../**` and v2's `/*` are equivalent here. The boundary
  resource v2 matches is "the canonical external directory boundary, normally
  ending in `/*`", which the trailing-star form covers whether opencode
  matches the boundary or the full path.
- v1's `list` rule is dropped: `list` is not in v2's action table
  (`/v2/docs/permissions` § Actions; only `read, edit, glob, grep, shell,
  subagent, skill, question, webfetch, websearch, external_directory,
  <server>_<tool>, execute`). A dead rule that looks alive is the failure mode
  this repo's permission history is about.
- v2 natively expands `$HOME`/`~/` only for `external_directory`, `read`, and
  `edit` resources — shell resources stay raw text, which is why no shell rule
  carries a path.
- Once the template emits native `permissions` and the chezmoidata carries no
  `permission` key, there is no legacy/native collision: v2's merger puts
  legacy-migrated rules before native ones and keeps the native value on
  conflict (`normalize.ts`).

## Key-by-key audit of the config (template + `.chezmoidata/opencode.yaml`)

| Key (source) | v2 fate | Evidence | Plan |
|---|---|---|---|
| `$schema: https://opencode.ai/config.json` (template) | v2 docs use the same URL | `/v2/docs/config` § Schema | Keep. The published schema still served the v1 shape on 2026-10-06 (no `permissions`/`update` in it), so editor validation may flag the array until upstream updates it; opencode itself ignores excess properties (`onExcessProperty: "ignore"` in the v2 loader). Re-check the schema on implementation day (open decision 6). |
| `share: "disabled"` (template) | native v2 enum `manual\|auto\|disabled`; accepted, but "session sharing is not supported yet" | v2 schema `Info.fields.share`; `/v2/docs/config` § Sharing | Keep as-is. |
| `autoupdate: "notify"` (template) | legacy key; v2 native key is `update` with enum `disable\|notify\|auto`; `"notify"` maps to `"notify"` | `normalize.ts` `LegacyAutoupdate` + migration table; `/v2/docs/config` § Updates | Replace with `"update": "notify"` (open decision 8 confirms the value). |
| `permission` (template) | legacy; migrated to ordered array, order preserved, `bash`→`shell` etc. | `migratePermissions`, `normalizeAction` | Migrate to native `permissions` array (section above). |
| `model: openrouter/z-ai/glm-5.3-flash` (chezmoidata) | parses: selection pattern `/^[^/#]+\/[^#]+(?:#[^#]+)?$/` splits provider `openrouter` / model `z-ai/glm-5.3-flash`; provider id unchanged (only `azure-cognitive-services` and `google-vertex-anthropic` are renamed) | `ConfigModel.Selection`; `providerID()` in `v1/config/migrate.ts` | Keep in chezmoidata, v1 shape — v2 parses it through its maintained legacy layer. |
| `small_model: ollama/qwen3:8b` (chezmoidata) | legacy; v2 has no native `small_model`. The migrator maps it to `agents.title.model` only | `normalize.ts` (`migratedSmallModel` → `legacyAgents.title`) | Keep for title locality. v1 used it for titles, summaries and compaction (template comment); v2's `summary` and `compaction` are separate shipped agents — add explicit `agents.summary.model` and `agents.compaction.model` entries in chezmoidata to keep "trivial calls never leave the box" (open decision 4; compaction model selection semantics not fully verified). |
| `provider.openrouter.models."anthropic/claude-opus-5"` with `options.reasoning.effort` and `variants {max,xhigh,medium}` (chezmoidata) | parses: v1 `Model.id` is optional (our entries are key-id'd, no `id` field); `options` → model `settings`; `variants` record migrates to an array of `{id, settings}` | `v1/config/provider.ts`; `migrateModel` in `v1/config/migrate.ts`; v2 `ConfigProvider.Model` (`modelID` optional) | Keep v1 shape. Verify the resolved shape with `opencode debug config` after install (the options/settings split helper `ConfigProviderOptionsV1` was not read line-by-line). |
| `agent.deep {description, mode: primary, model, variant: max}` (chezmoidata) | parses: v1 agent schema accepts all four fields; `model`+`variant` fold into a v2 model selection | `v1/config/agent.ts`; `migrateAgent`/`modelSelection` | Keep v1 shape. Native v2 form would be `agents.deep.model: "openrouter/anthropic/claude-opus-5#max"` — recorded here for a future chezmoidata rewrite, not this migration. |
| keys with no v2 native form (`logLevel`, `server`, `subagent_depth`, `layout`, five `experimental.*` flags) | dropped with diagnostics | `unsupportedTopLevel`/`unsupportedExperimental` in `normalize.ts` | Not used by this config — no action. |

Net: `.chezmoidata/opencode.yaml` needs **no change** for this migration (only
the optional small-model follow-up in decision 4). The legacy layer is
explicitly maintained upstream — the file header's merge caveat stays true, and
the template comment pointing at it stays true.

## Machine-local state (sessions, auth)

- v1 keeps sessions in `~/.local/share/opencode/opencode.db` and tokens in
  `~/.config/opencode/auth.json` (per this repo's topic README and remove.yaml
  comments). v2 resolves the same XDG roots for app name `opencode`
  (`packages/util/src/global.ts`): data `~/.local/share/opencode`, config
  `~/.config/opencode`, plus `OPENCODE_CONFIG_DIR` override.
- v2 migrates sessions in place, automatically, on first run: it opens the
  database, sees v1's `session` table, applies schema migrations, and
  transforms sessions/messages/parts into `session_v2`, recording progress in
  KV `migration.v1-v2` (`v1-migration.bun.ts`). Rows that fail to decode are
  skipped with a warning, not fatal. A prior `opencode-next.db` (v2 preview
  data) is also imported if present.
- v2 stores credentials in a sqlite `credential` table keyed by integration
  (`credential.ts`, `integration.ts`). The `auth import` command consumes
  `auth export` JSON — not v1's `auth.json`. I found no v1 auth.json import in
  the code read, so plan for a re-auth (`/connect` in the TUI, or the key
  flow) and verify with `opencode auth list` after install. `auth.json` itself
  is untouched by anything found here, so it survives for a v1 rollback.
- Because the session migration is in place, back up `~/.local/share/opencode/`
  before the first v2 run — the rollback section explains why.

## Brew mechanics (install / remove)

- Formula verified today: `opencode-v2.rb` — version 2.0.24,
  `depends_on "ripgrep"`, `conflicts_with "opencode", because: "both install
  an opencode binary"`, installs `bin.install "opencode"`. Ripgrep arrives as
  a brew dependency, so `topic_requires` stays `[homebrew, node]`.
- `conflicts_with` makes brew refuse the install while v1 is present, so
  `install.yaml` gains an uninstall step **before** the install step:
  `community.general.homebrew` with `name: "{{ opencode_tap }}/opencode"`,
  `state: absent` — idempotent (no-op when v1 was never installed). Brew's
  refusal names the conflict, so a machine with a homebrew/core `opencode`
  (not this box's situation) fails with a readable error rather than silently.
- Tap tasks unchanged: same tap (`opencode_tap: anomalyco/tap`), same
  trust-before-tap ordering (Homebrew 7 refuses untrusted taps — the topic's
  documented 2026-09-14 finding).
- Trust entries: `brew install` writes a formula trust entry next to the tap
  entry (topic README, measured 2026-09-14). After migration the formula entry
  is `anomalyco/tap/opencode-v2`; `remove.yaml`'s `brew untrust --formula`
  line renames accordingly. The v1 formula's trust entry lingers on machines
  that ever installed v1 — open decision 2 proposes cleaning it opportunistically.
- Teardown mirrors the new state in the same commit (spec § Layering;
  TOPICS.md CRUD invariant): uninstall `opencode-v2`, untrust the v2 formula,
  same gated untap/untrust-tap pair, skill teardown unchanged. The "left in
  place" debug note updates to mention v2's sqlite and the in-place session
  migration.

## Upgrade lifecycle

`apps/homebrew/tasks/upgrade.yaml` runs `upgrade_all: true` with
`upgrade_options: formula`, which covers tap formulae — v2 included. So the
topic's `upgrade.yaml` stays an empty stub (binary currency is brew's), and
the skill-sync tasks keep `[opencode_skills, upgrade]` in install.yaml. This
is TOPICS.md § "Where upgrade logic lives" applied unchanged; confirm nothing
regressed by running the topic resolution tests after the change.

## Files that change

| File | Change |
|---|---|
| `dotfiles/apps/opencode/tasks/install.yaml` | Add "remove conflicting v1 formula" task before the install task; install task targets `{{ opencode_tap }}/opencode-v2`; comments updated (conflicts_with rationale; v2 on the same pinned tap). Skill-sync tasks untouched. |
| `dotfiles/apps/opencode/tasks/remove.yaml` | Uninstall and formula-untrust retarget `opencode-v2`; optionally also untrust the v1 formula name (decision 2); "not removed" note updated for v2 state. |
| `dotfiles/apps/opencode/tasks/upgrade.yaml` | Comment only: binary is now the v2 formula, still brew-owned. |
| `dotfiles/apps/opencode/defaults/main.yaml` | Comment only: the tap note now covers both formulae; no variable changes. |
| `dotfiles/apps/opencode/README.md` | Binary section (v2 formula, conflict removal in-run), config section (permissions array, `update`, `$HOME` expansion), teardown, first-run (sessions auto-migrate; re-auth likely). |
| `dotfiles/apps/opencode/CHANGELOG.md` | Dated entry: breaking_changes (v1 formula removed by install; config keys renamed; re-auth likely), minor_changes (v2 install), known_issues (auth.json import not found; bash allowlist behavior change explained). |
| `dot_config/opencode/opencode.jsonc.tmpl` | `permission` map → `permissions` array (exact mapping above); `autoupdate` → `update`; comments updated; `.chezmoidata` pointer comment kept. |
| `.chezmoidata/opencode.yaml` | No change for this migration; optional small-model additions per decision 4. |
| `topic.yml` | No change. |

## Commit sequence (inert first, activating last)

1. **Topic commit** — `tasks/install.yaml`, `tasks/remove.yaml`,
   `tasks/upgrade.yaml`, `defaults/main.yaml`, `README.md`, `CHANGELOG.md`.
   Tree stays coherent alone: the next run-role would install v2 and remove v1
   while the deployed config is still v1-shaped — which v2 tolerates (legacy
   layer, verified), and chezmoi still deploys the v1 config for any v1
   machine. Teardown lands in the same commit as the install change (spec §
   Layering).
2. **Config commit** — `dot_config/opencode/opencode.jsonc.tmpl` (+ the
   optional chezmoidata item if decided). This is the activating commit: it
   changes behavior on the next `chezmoi apply`. Order matters: the topic
   commit first means a lone `chezmoi apply` between commits cannot produce
   "v1 binary + v2-only config", the one combination the migration has not
   verified.

Both commits land in one PR: the template deploys to `~/.config/opencode` and
carries permission rules, so § Merge gates puts it under human review
(deployed-tree file + policy path), and the topic tasks are the other half of
the same decision.

## Verification

Static (render level, both legs per AGENTS.md § Verification):

- Render the template under both `os_family` values (Darwin, Debian) with
  Jinja `StrictUndefined`, strip JSONC comments, and assert: valid JSON;
  top-level `permissions` is an array and `permission` is absent; `update`
  present / `autoupdate` absent; `share: "disabled"`; the shell rules in
  mapping order (catch-all first, `find` denies after `find *`); the
  external_directory trio deny-first/allow-last with literal `$HOME` strings
  identical under both OS legs (no `.chezmoi.homeDir` left inside the
  permissions block); model/provider/agent legacy keys still emitted from
  chezmoidata.
- Extend `tests/topics/test_opencode_config_layers.py` (it already renders
  with chezmoi and strips JSONC) and
  `tests/topics/test_opencode_os_agnostic.py`; keep
  `tests/topic_resolution/test_opencode_both_os.py` green unchanged; guards
  tests (`tests/guards/`) untouched — the dotagents flow is identical.
- New static tests for the tasks: `anomalyco/tap/opencode-v2` appears in
  install and remove; the v1 uninstall task precedes the v2 install; the
  formula-untrust task names `opencode-v2`.
- Every new test is seen to fail first: mutate the template (drop the find
  denies, flip an effect, reintroduce `permission`) and mutate the task files
  (swap the formula name, reorder the uninstall), record `Mutation:` and
  `Failing-test:` trailers on the implementation commit.

Runtime (author-run or implement-agent read-only, after the binary lands):

- `brew info anomalyco/tap/opencode-v2` → 2.0.x; `brew list --versions |
  grep opencode` → v2 only.
- `opencode --version` → 2.x.
- `opencode debug paths` — v2 CLI has this handler (verified in
  `packages/cli/src/index.ts`); confirms the data/config dirs.
- `opencode debug config` — shows the normalized config; confirms provider
  models, variants, the `deep` agent, `agents.title` from `small_model`, and
  the `permissions` array with no normalization diagnostics for our keys.
- Session history: open the TUI, check prior sessions listed.
- `opencode auth list` — if empty, re-auth (`/connect`).

## Author-run follow-up steps (machine state, never agent)

Order matters: ansible before chezmoi apply, so v2 always meets a config it
can parse, and nothing upgrades the deployed config before the binary exists.

```bash
# 0. Back up machine-local state (rollback insurance — see below)
cp -a ~/.local/share/opencode ~/.local/share/opencode.pre-v2-backup
cp -a ~/.config/opencode/auth.json ~/.config/opencode/auth.json.pre-v2 2>/dev/null

# 1. Install v2, remove v1 (run-role is cwd-dependent — from inside dotfiles/,
#    per the 2026-10-03 observation)
cd ~/dotfiles && ./run-role.sh opencode

# 2. Verify the binary
command -v opencode && opencode --version        # 2.x, from the brew prefix

# 3. Deploy the migrated config (apply the specific path, not the tree)
chezmoi apply ~/.config/opencode

# 4. Verify the config loads and migrated cleanly
opencode debug config                            # permissions array, no diagnostics
opencode auth list                               # re-auth if empty (/connect)

# 5. Remove the mise shadow (repo mise config has no opencode entry — checked
#    2026-10-06; the shadow lives in the user-global config or a bare install)
mise ls opencode                                 # find the 1.18 version
grep -n opencode ~/.config/mise/config.toml      # remove the declaration line if present
mise uninstall opencode && mise reshim           # drop versions and stale shims
hash -r && command -v opencode                   # must now resolve to the brew prefix
```

## Rollback

- **Binary:** `brew uninstall anomalyco/tap/opencode-v2 && brew install
  anomalyco/tap/opencode` — the v1 formula is still on the tap (verified
  2026-10-06). v1's trust entry is intact unless decision 2 cleaned it
  (re-trust is one command).
- **Config:** `git revert` the config commit, `chezmoi apply
  ~/.config/opencode`. v1 loads its own schema again.
- **Sessions:** the v2 migration runs in place, so a migrated database may not
  be readable by v1 1.18 — restore `~/.local/share/opencode/` from the
  pre-v2 backup taken in step 0. Sessions created after the migration exist
  only in v2; that loss is bounded and accepted. `auth.json` is never touched
  by the v2 code paths found here, so tokens survive on both sides.
- **Topic:** `git revert` the topic commit and re-run `./run-role.sh opencode`
  from `~/dotfiles` — it reinstalls v1; note `conflicts_with` runs the other
  way, so v2 must be uninstalled first (the revert already did that if
  applied; otherwise `brew uninstall anomalyco/tap/opencode-v2` by hand).

## Open author decisions

Safe defaults are stated so the implement agent is not blocked; each can be
overridden by editing the plan line before implementation starts.

1. **The trailing bash `"*": "ask"` (template line 69).** The file's own
   comment says the trailing catch-all was the pre-2026-09-16 bug, yet the
   line is still present, so today's live behavior (everything asks) contradicts
   the comment. Default: treat it as leftover — the migrated array expresses
   the 2026-09-16 intent and drops it. If it was deliberate, the shell group
   collapses to the single ask rule.
2. **v1 formula trust residue on install.** Machines that ever installed v1
   keep a trust entry for `anomalyco/tap/opencode` after the topic uninstalls
   the formula. Default: `install.yaml` also runs the idempotent
   `brew untrust --formula {{ opencode_tap }}/opencode` after the removal
   (harmless when absent, converges both eras).
3. **`read *` allow vs v2's `.env` protection.** v2's built-in base policy asks
   before reading `*.env*`; a global `read * allow` (appended after the base)
   overrides that. Default: keep v1 parity (reads free) and say so in the
   template comment, so a future tightening is a one-line edit.
4. **Small-model locality for summary and compaction.** v2 maps legacy
   `small_model` to the `title` agent only. Default: add
   `agents.summary.model` and `agents.compaction.model` entries to
   `.chezmoidata/opencode.yaml` (both `ollama/qwen3:8b`) to keep the recorded
   "trivial calls never leave the box" intent. Compaction model selection
   semantics in v2 were not fully verified — confirm with `opencode debug
   config` on the day.
5. **`default_agent`.** v1 never set one; v2 falls back to `build` when unset.
   Default: leave unset (parity); `deep` stays switchable.
6. **`$schema` URL.** v2's docs still point at `https://opencode.ai/config.json`,
   which served a v1-shaped schema on 2026-10-06. Default: keep the URL (v2
   ignores excess properties; editor validation is the only gap). Re-check
   whether the published schema has been updated before the config commit.
7. **`list` rule.** Not a v2 action. Default: drop it and leave a comment
   naming why (a rule that can never match is indistinguishable from a strict
   one — AGENTS.md § Machine-specific values).
8. **`update` value.** Default: `"update": "notify"` — v1 parity, and the v2
   default anyway; brew remains the upgrade path, so `auto` stays off.

## Not verified

Named plainly, per spec § Evidence:

- The exact production database filename/path wiring (the database layer I
  read defaults to `:memory:`; the migration code reads v1's tables from the
  database it opens, which implies the same in-place file under
  `~/.local/share/opencode`, but I did not find the bootstrap that passes the
  real path). `opencode debug paths` settles it on the day.
- Whether anything in v2 imports v1's `auth.json`: not found in
  `credential.ts`, `integration.ts`, `provider.ts`, the v1-migration module,
  or the `auth import` handler. Treat re-auth as required until proven
  otherwise on the box.
- How v1 1.18 behaves when handed the migrated v2 config. Mitigated by the
  author-run order (ansible first), not resolved.
- What models v2's `summary` and `compaction` agents use by default, and how
  compaction picks its model. The compaction guide was not fetched; decision 4
  carries the check.
- That `brew install` writes a formula trust entry for `opencode-v2` the same
  way it did for v1 (measured for v1 on 2026-09-14; same mechanism assumed).
- `ConfigProviderOptionsV1`'s options/settings/headers split (our `reasoning`
  block was validated by schema shape, not by reading the splitter). Confirm
  with `opencode debug config`.
- Whether `opencode.ai/config.json` has been updated to the v2 shape
  (open decision 6 re-checks on implementation day).