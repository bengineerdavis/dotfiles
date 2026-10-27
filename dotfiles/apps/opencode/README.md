# opencode

Installs [opencode](https://github.com/anomalyco/opencode), the terminal AI
coding agent.

## What it manages

| Layer    | State                                              | Owner     |
|----------|----------------------------------------------------|-----------|
| Ansible  | the `opencode` binary, from the pinned tap          | this topic |
| chezmoi  | `~/.config/opencode/opencode.jsonc`                 | `dot_config/opencode/` in the chezmoi source |
| nobody   | `~/.config/opencode/auth.json`, `opencode.db`, `node_modules` | machine-local, never versioned |

Layering: Ansible installs and triggers; chezmoi owns the config file; the
binary's own state (`auth.json` tokens, `opencode.db` session history) is
machine-local and no topic touches it on install or remove.

The global skill set is **not** this topic's. It is user-global, every agent
runtime loads it, and it is owned by [`apps/dotagents`](../dotagents/README.md).

## The binary

Installed from `anomalyco/tap` as `opencode-v2` (2.0.x), named explicitly
(`anomalyco/tap/opencode-v2`) because homebrew/core carries a same-named v1
formula and the tap is the one that tracks releases. Measured 2026-09-14: tap
1.18.31, core 1.18.30 — core's formula sets `livecheck { throttle 5 }`, so it
follows every fifth release and trails upstream by design.

The v2 formula declares `conflicts_with "opencode"` — both install an
`opencode` binary — so brew refuses the v2 install while v1 is present.
`install.yaml` therefore uninstalls the v1 formula first, in the same run,
and cleans its leftover formula trust entry (`brew untrust --formula`,
decision 2's safe default, 2026-10-06). A machine carrying a homebrew/core
`opencode` rather than this tap's fails with brew's readable conflict error
instead.

A second install channel can shadow this binary — see the CHANGELOG
known_issues entry dated 2026-10-19 before trusting `opencode --version`.

### The tap must be trusted first

Homebrew 7 refuses to load formulae from a third-party tap until the tap is
trusted, and **the refusal surfaces at tap time, not install time**. `brew tap`
validates every formula in the tap, refuses each one, and aborts with:

```
Error: Cannot tap anomalyco/tap: invalid syntax in tap!
```

which names neither trust nor the fix. So `install.yaml` runs
`brew trust --tap anomalyco/tap` *before* the tap task. Trust is a config entry
keyed by name (`~/.homebrew/trust.json`, or `$XDG_CONFIG_HOME/homebrew/trust.json`
when that is set), not a property of tap contents, so trusting an untapped tap
is valid — and it is the only ordering that works.

No Ansible module covers this; `homebrew_tap` predates brew's trust store, so
the task is a raw command. It is idempotent: a second run exits 0 and reports
`Already trusted tap`.

Trusting a tap lets brew execute its Ruby. This tap is upstream opencode's own
(`anomalyco/opencode` ships it via GoReleaser), so trusting it is trusting the
vendor whose binary we are installing regardless.

Darwin uses the homebrew topic. Debian resolves `homebrew` through the PATH
check — this box runs linuxbrew, and a fresh Debian box needs linuxbrew
installed before this topic can run. The install task fails with that named
fix if brew is absent.

## The skill set

Moved. The approved-source list, the trust allow-list, the excludes, the
vendored exceptions and the dotagents sync now live in
[`apps/dotagents`](../dotagents/README.md). This topic no longer carries a skill
manifest, and installing it alone does not install or refresh skills.

## The config

`~/.config/opencode/opencode.jsonc` deploys from
`dot_config/opencode/opencode.jsonc` and carries the cross-machine baseline:
privacy (`share: disabled`), model defaults, and the v2 `permissions` array
(`update: notify` replaced v1's `autoupdate`). The permission rules are
order-sensitive — v2 takes the LAST matching rule — so they stay literal in
the template rather than in `.chezmoidata`, whose merge would reorder them.
The `external_directory` rules carry literal `$HOME/...` globs: v2 expands
`$HOME` itself when the config loads, so templating the home directory would
bake one machine's path back in. Per-machine choices (auth, per-project
overrides) stay out of it. Measured on 2026-09-12: when both `opencode.json`
and `opencode.jsonc` exist, jsonc wins, so the chezmoi-managed file is
authoritative.

## Teardown

`--tags remove` uninstalls the binary. The tap is guarded behind a flag that
defaults to false — flip it deliberately:

- `opencode_remove_tap` — untap **and** untrust `anomalyco/tap` (one flag: brew
  needs the tap trusted to load it, so install creates both, and revoking trust
  while the tap is still present would break anything else installed from it).
  Two untrusts, not one: `brew trust --tap` writes the tap entry and `brew
  install` writes a separate formula entry (now `anomalyco/tap/opencode-v2`),
  and `brew untrust --tap` does not remove the latter — measured on Homebrew
  7.0.1, 2026-09-14. The uninstall targets the v2 formula; a v1 formula's
  trust residue is cleaned idempotently by the next install run instead.

The global skill set is untouched by this teardown; remove it through
`apps/dotagents`.

```bash
ansible-playbook apps/opencode/playbook.yaml --tags remove
ansible-playbook apps/opencode/playbook.yaml --tags remove \
  -e opencode_remove_tap=true
```

## First run on a new machine

1. Provision chezmoi (deploys the config) and the topics this machine needs.
2. `./run-role.sh opencode` — or the parent playbook with `--tags provision`.
3. `opencode auth login` — tokens are machine-local by design.
4. Skills come from `./run-role.sh dotagents`, or from the same parent run.

The v2 migration changes what first run means (2026-10-06): v2 opens the same
data directory and migrates v1 sessions in place on the first launch, so back
up `~/.local/share/opencode/` before it — a migrated database may not be
readable by v1 again. Tokens move to a sqlite credential store, and no import
of v1's `auth.json` was found in the v2.0.24 source, so plan on a re-auth;
`opencode auth list` tells. `auth.json` itself is untouched by anything in
v2, so it survives for a v1 rollback.
