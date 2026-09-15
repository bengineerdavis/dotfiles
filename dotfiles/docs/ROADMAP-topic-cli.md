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


---

# Amendment — 2026-09-14

The 2026-09-09 design above stands on dispatch shape, the `~/bin` compatibility
rule, and the verified Chrome constraints. This amendment records decisions it
did not cover, taken deliberately rather than by drift. Where the two disagree,
this section wins and says so.

## The tool is called `topical`

`topic` becomes **`topical`**. Topics are the coconuts; the config is the trunk.
It also stops the binary sharing a name with the domain noun, which was going to
make every sentence in this document ambiguous.

The file keeps its `ROADMAP-topic-cli.md` name until the tool exists, because
`TASKS.md` references it by path and a rename would be churn for nothing.

## One CLI, commands split between deterministic and agent

Not two binaries. `topical` has deterministic verbs and agent verbs in one
command surface. The CLI is for people who prefer it, for when no agent is
available, and for opening a live session with the agent.

The preferred path is still to hand work to the agent and let it decide — the
agent knows the skills and the CLI. The deterministic verbs are what it drives,
and what a human drives when the agent is unavailable or unwanted.

## Drift between CLI and MCP: solved by a choice, not a process

The agent reaches `topical` **both** ways: it shells out to the CLI, and the
same commands are exposed over MCP for tools that speak it. That interoperates
with things neither of us has thought of yet, which is the point.

Two interfaces normally means two things to keep in step. This one does not,
provided a decision is made now:

> **Write `topical` with Typer, not argparse.**

Researched 2026-09-14 rather than assumed. `pycli-mcp` (PyPI 0.4.0, "MCP server
for any Python command line application") and `click-to-mcp` both **introspect a
Click/Typer app at runtime** and expose each command as an MCP tool with a
matching parameter schema. The CLI stays the single source of truth; the MCP
tool list is derived, not maintained. Adding a verb adds a tool with no second
edit, so drift is not policed — it is impossible.

argparse is the one parser this does not work with: `pycli-mcp` marks argparse
support experimental, and it lacks the introspection hooks the reflection
depends on. `browser-ext` is argparse (`:55`, `:769`) and stays that way — it is
a topic tool, not the dispatcher. Typer is already a repo dependency (`bin/binned`
uses Typer and questionary), so this adds nothing new to install.

The alternative — `fastmcp generate-cli`, which reads MCP tool schemas and
writes a CLI — was rejected for the same reason inverted: it makes the MCP
schema authoritative and the CLI generated, and here the CLI is the thing humans
and the agent both use directly.

**Caveat worth keeping:** MCP guidance favours tools designed around meaningful
operations rather than a copy of every subcommand and flag. If reflected verbs
ever read badly as tools, the fix is to shape the *CLI* verbs better, not to
hand-write a divergent tool list.

## Agent backends register like `llm` model plugins

`topical agent` opens a live session, preferring an installed backend and taking
`--with claude|opencode` to force one. But backends are **registered, not
hardcoded** — the model is `llm`'s plugin system, where an engine declares
itself and becomes selectable.

Each backend declares how it is launched (`claude --agent topical`,
opencode's equivalent). Configure once; do not pass it every time. The explicit
per-invocation form stays for debugging and for doing it by hand.

This is also what makes "other agents integrate with it" a config entry rather
than a code change, which is the same property `topic_cli:` gives topics.

## The agent ships as a plugin, from its own repository

The agent, its skills and its commands are **one Claude Code plugin** —
`.claude-plugin/plugin.json` with `agents/`, `skills/`, `commands/`, and
optionally `.mcp.json`. Verified 2026-09-14: plugins do ship subagents, as
markdown with `name`/`description`/`model`/`effort`/`maxTurns` frontmatter,
surfacing under scoped names like `topical:topical`.

Distribution is **dotagents**, which `add` resolves as plugins first, then
skills. This repo declares it as a dependency the same way `apps/opencode`
already declares its skill sources.

It lives in **its own repository**, not here and not in `ai-prompt-library`.
That keeps `AGENTS.md`'s ladder intact — AI work is not authored in the
provisioning repo — without making the prompt library own a tool that is really
about machine configuration.

Two directions recorded now so they are not rediscovered, neither in scope:

- **The prompt library learning to host skills and agent files as components**,
  so this repo's own skills could live there as first-class parts. That is a
  roadmap item for *that* project, not this one.
- **Installing `topical` as a uv tool from PyPI**, with a parallel topic
  treating it like any other Python tool this machine pulls in. That is the
  natural end state once it is a real package, and it is how the rest of the
  `pipx:` entries in `apps/mise` already work.

## Shrinking the agent is a ratchet, and it must be visible

The agent's surface should shrink over time, until only what genuinely needs
adaptation, heavy context, or agent-only ability is left. That only happens if
graduation is visible, so two mechanisms, both **opt-in**:

1. **Each agent-only capability names its deterministic replacement.** A line
   saying what would have to exist for this to become a plain verb, and why it
   cannot be one yet. Graduating it is then a diff: delete the note, add the
   verb.
2. **Record which verbs the agent actually invokes**, so repeated deterministic
   sequences surface as refactor candidates from evidence rather than taste.

Both land as **pull requests for review**. Neither replaces a skill, a command
or code silently — least of all for the maintainer, who is the person most
likely to be surprised by their own tooling changing underneath them.

### Unhandled errors become offers, never actions

When the agent hits an error it does not handle or did not expect, it may
**offer** to escalate it as a PR against this repository — after checking there
is not already one open for it. Offer, not act.

This is the same posture `TASKS.md` already sets for `dotfiles-triage`: diagnose
and propose, never self-apply. Two features arriving at the same rule
independently is a good sign it is the right one.
