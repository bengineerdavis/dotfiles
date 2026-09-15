# ROADMAP: the `topic` CLI

**Status: designed, not built.** This is a handoff document. Nothing described
under "MVP" exists yet; everything under "What already exists" does and is
working. Written 2026-09-09.

## Why this exists

`apps/chrome` was built to let Ansible install and maintain browser extensions.
Doing that surfaced two jobs that are not Chrome-specific and not really
Ansible's either:

1. **Scaffolding a topic.** `./init-config.sh <name>` copies `template_dir/`
   and stops. Every field in `topic.yml` is then edited by hand, and the five
   lifecycle files start as comment-only stubs. A new browser topic (firefox is
   the next one) repeats all of it.
2. **Editing a topic's manifest.** `apps/chrome/files/browser-ext add` proved
   this is worth automating — it validates the ID, resolves the name, pins the
   latest tag, and appends to `defaults/main.yaml` without destroying the
   comments. But it lives inside the chrome topic and only knows about browsers.

`topic` is the front door for both. **MVP is those two jobs and nothing else.**

## What already exists (do not rebuild)

| Thing | Where | State |
|---|---|---|
| chrome topic | `apps/chrome/` | Working, idempotent, applied |
| Extension manifest schema | `apps/chrome/defaults/main.yaml` | Working; browser-agnostic by design |
| `browser-ext` CLI | `apps/chrome/files/browser-ext` | Working: `status`/`drift`/`seeds`/`add`/`sync` |
| Scaffolder | `init-config.sh` + `template_dir/` | Working but minimal |
| IDE extension notes | `apps/chrome/TODO-ide-extensions.md` | Deferred, not designed |

Read `apps/chrome/README.md` before touching any of this. It records the
constraints below in full.

### Constraints that are verified, not assumed

These were each confirmed against this machine or Google's documentation. Do not
re-litigate them; do re-verify if Chrome's major version moves substantially.

- **`--load-extension` is gone** from branded Chrome as of v137 (this machine
  runs 152). It still works in Chromium and Chrome for Testing.
- **macOS refuses off-store external installs**: "as of Chrome 44, no external
  installs are allowed from a path to a local CRX file on Mac OS." On macOS an
  `external_update_url` must point at the Web Store. This is why the schema has
  a `store` / `git` split rather than one install path.
- **`Secure Preferences` is HMAC-signed** (per-entry MACs plus `super_mac`).
  Chrome resets the block if anything else writes it. This is why the CLI only
  ever *reports* extension state and never mutates it.
- **Off-store force-install IS possible on this machine.** Google's rule: it
  works only where the instance is "managed via MDM, joined to a domain via MCX
  or enrolled in Chrome Enterprise Core." This machine is Kandji MDM-enrolled
  *and* Chrome Enterprise Core-enrolled. The blocker is authority, not
  capability — the policy must come from the org's IT admin console or Kandji.
  A local `defaults write` lands as recommended-tier, which
  `ExtensionInstallForcelist` ignores.
- **Unpacked extension IDs are a hash of the load path.** Loading the same
  extension from a new folder registers a *new* extension. This is the single
  most important constraint in the design and the reason `chrome_unpacked_root`
  exists.

## MVP scope

Two commands. Resist adding a third.

### 1. `topic new <name>`

Replaces `init-config.sh` with something that finishes the job.

```
topic new firefox --tier app --os Darwin --requires homebrew
topic new firefox --from chrome        # clone an existing topic's shape
```

Must:
- scaffold from `template_dir/` (keep using it; do not fork a second template)
- fill in `topic.yml` from flags rather than leaving `<topic>` placeholders
- substitute the topic name through the lifecycle files' header comments
- refuse to overwrite an existing `apps/<name>/`
- **not** create `main.yaml` at the role root — only 6 of 26 topics have it and
  it is dead scaffold (it was removed from `apps/chrome`)
- create `defaults/main.yaml` and `vars/main.yaml`, since 26/26 and 25/26 topics
  respectively have them

`--from <topic>` is the one that matters for firefox: it should copy the
manifest *schema* and the lifecycle structure without copying chrome's
extension entries or its Chrome-specific task bodies.

### 2. `topic <name> ext add ...`

Generalises `browser-ext add` so it works against any topic that declares an
extension manifest.

```
topic chrome  ext add store <id-or-webstore-url> [--name N] [--why W]
topic firefox ext add git <repo-url> [--slug S] [--ref R] [--build C] [--load-subdir D]
```

The existing implementation in `apps/chrome/files/browser-ext` already does all
of this and is already `--topic`-aware. **MVP is wiring, not rewriting.**

The one piece of real work: `browser-ext` currently hardcodes Chrome's profile
layout (`~/Library/Application Support/Google/Chrome`) for the `status`/`drift`
paths. `add` does not depend on that and can be lifted as-is; the reporting
verbs need the browser-specific bits pushed behind a small adapter before
firefox can use them. **Do `add` first — it is the MVP; leave the reporting
verbs Chrome-only until firefox actually needs them.**

## Dispatch design

The recommendation is a **git-style dispatcher**, not a monolith.

`topic` resolves `topic <name> <noun> <verb> ...` by reading
`apps/<name>/topic.yml` for a new optional key:

```yaml
topic_cli:
  ext: files/browser-ext      # `topic chrome ext ...` execs this
  models: files/ollama-models # `topic ollama models ...` execs this
```

and then `exec`s that script with the remaining argv, plus `--topic <name>`.

Why this shape:

- **Topic tools stay self-contained**, which is the doctrine the whole repo runs
  on (`docs/TOPICS.md`). Adding a topic never means editing a central file.
- **Every tool keeps working standalone.** `browser-ext status` still runs. That
  matters enormously for migration — see the compatibility section.
- **`topic.yml` is already the metadata file** the parent playbook slurps on
  every run, so there is one place topics describe themselves, not two.
- A monolith was considered and rejected: it would centralise what the repo
  deliberately distributes, and would make `topic` a merge-conflict magnet.

Reserved first words (`new`, `list`, `doctor`, `help`) are checked before topic
names. `topic doctor` should validate that no topic is named a reserved word.

### Where `topic` itself lives

Recommendation: `apps/topic/files/topic`, symlinked to `~/bin/topic` by its own
`install.yaml`, exactly like every other topic-owned tool. Self-hosting is a
little odd but it keeps the CRUD ownership invariant intact and means `topic`
arrives the same way everything else does.

It finds the repo root by resolving its own symlink (`files/topic` →
`apps/topic/` → repo root), which is the trick `browser-ext` already uses to
locate its manifest. Do not require a `DOTFILES_ROOT` env var.

## Migration inventory — and why MVP does not touch it

Six tools are topic-owned symlinks in `~/bin` today:

| Tool | Topic | Subcommands |
|---|---|---|
| `browser-ext` | chrome | status, drift, seeds, add, sync |
| `ollama-models` | ollama | sync, status, check, prune |
| `ollama-role` | ollama | get, env, serverenv, list, check |
| `ollama-usage` | ollama | report, ctx, snapshot, history |
| `ollama-bench` | ollama | run, show |
| `ollama-evals` | ollama | run, cases, show, coverage |

**Renaming any of them is a breaking change.** Verified references:

- `playbook.yaml:291,303` calls `~/bin/ollama-models sync` in `post_tasks`
- `apps/ollama/tasks/remove.yaml:160-161` removes `~/bin/ollama-bench`,
  `~/bin/ollama-role` by absolute path
- `.claude/settings.local.json` allowlists `ollama-role get *`,
  `ollama-evals cases *`, `~/bin/ollama-bench run *` and others by name
- launchd labels embed the name: `com.ollama-usage.snapshot`

So: **the dispatcher adds a front door; it does not close the old one.** Both
`topic ollama models sync` and `ollama-models sync` must work. The `~/bin`
symlinks stay. If they are ever retired it is a separate, deliberate change with
its own audit of the four reference classes above — not a side effect of adding
a CLI.

## Firefox — the next topic, and why it is not a copy of chrome

Everything in the manifest *schema* transfers. Almost nothing in `tasks/` does.
Flagged as **to verify**, not as established fact — the next agent should
confirm each before building:

- Firefox has no External Extensions JSON mechanism. Its equivalents are the
  `Extensions` policy in `policies.json`, a distribution directory, or dropping
  XPIs into a profile's `extensions/`. Which of these works unprivileged on
  macOS needs checking.
- Firefox requires extensions to be **signed by Mozilla** on release builds.
  This is the analogue of Chrome's off-store restriction and is likely to be the
  dominant constraint — an unsigned local build may need Developer Edition,
  Nightly, or `xpinstall.signatures.required=false`, none of which are free
  choices.
- Firefox profiles live in `~/Library/Application Support/Firefox/Profiles/` with
  a `profiles.ini`, not Chrome's `Local State` JSON. The `profiles()` function in
  `browser-ext` needs an adapter, not a tweak.
- `apps/firefox` already exists as an app-tier topic that only installs the cask.
  Extend it; do not create a second topic.

## Explicitly out of MVP scope

- Absorbing the five `ollama-*` tools behind `topic` (dispatcher will support it;
  do it after MVP proves the shape)
- `topic list`, `topic doctor`, `topic run`
- Editor/IDE extensions — see `apps/chrome/TODO-ide-extensions.md`
- Retiring any `~/bin` name
- Making `browser-ext`'s reporting verbs browser-agnostic

## Open questions — answered 2026-09-14

A1 in `TASKS.md` asked for these to be answered in the roadmap rather than in a
conversation. They are. The questions are kept verbatim above their answers so
the reasoning stays checkable.

**1. Should `topic new` also register the topic somewhere, or is the parent
playbook's directory scan enough?**

No registration. Verified at `playbook.yaml:50-56`: the parent playbook runs
`ansible.builtin.find` over `apps/` for `topic.yml`/`topic.yaml` with
`recurse: true, depth: 2` on every run. A topic is discovered by existing. A
registry would be a second source of truth able to disagree with the
filesystem, which is the drift this repo avoids everywhere else. **Nothing to
build.**

One boundary: topic *bundles* may want a list, since a bundle is a grouping that
does not exist on disk as a directory. That is bundle-level state and lives
outside topics by design — it is not an argument for registering topics.

**2. Does `topic <name> ext add` write to `defaults/main.yaml` directly, or
round-trip through the dispatcher's own validation first?**

Both, and `browser-ext` already works this way — this question describes a
choice that was already made correctly. It parses with `yaml.safe_load` to
validate (`executable_browser-ext:180`) and writes by text append
(`:226`), whose docstring gives the reason: *"this file is more comment than
data, and every one of those comments explains a constraint someone paid to
discover. A dump would delete all of them."*

Keep both halves. Researched 2026-09-14 rather than assumed: `ruamel.yaml`
round-trip mode is the serious alternative and **would** work here, because it
only loses comments under structural surgery (deleting keys, removing list
entries) and `add` does neither. It is rejected anyway on evidence — Red Hat's
Linux System Roles adopted ruamel for exactly this problem, converting commented
Ansible YAML, and still report comments not indented correctly, line wrapping
not preserved, and embedded scripts mis-indented. Text append loses none of
that, and costs no dependency.

**Revisit when, not if:** the moment `topic` needs to *remove* or *reorder*
manifest entries, text editing stops being tractable and ruamel's `.ca` comment
handling starts earning its cost. Adding is append-only; that is the whole
reason this works.

**3. Is `ext` the right noun for firefox too, or does it want `addon`?**

Both. `ext` is canonical, `addon` is an alias. Mozilla's vocabulary is "add-on"
and Chrome's is "extension"; an alias is one line in dispatch and spares every
user the other project's jargon. Costs nothing, so there is no trade to weigh.

**4. Fintastic: publish to the Web Store as unlisted?**

**Not an agent's call, and not a blocker.** It is a conversation with the repo
owner (trjuntunen) about how someone else's extension gets published. Recorded
here so it is not rediscovered: doing it would collapse a `git` entry to a
`store` entry and delete a category of work, but it changes nothing about the
CLI's shape. Build as if it will not happen.

### Also settled by A1: what `topic` is written in, and where it lives

`apps/topic/files/topic`, symlinked to `~/bin/topic` by its own `install.yaml`,
as the recommendation above says. **Python, as a PEP 723 `uv run --script`** —
not a new decision so much as the one `browser-ext` already made: it is 816
lines of exactly that, and `topic` is a dispatcher that will only grow. This is
the repo's documented rule (`AGENTS.md` § Languages: bash while a script is
small, Python once it is not) landing on the obvious side.

