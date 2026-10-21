# `skill-trust`

Decides whether an agent skill may be installed on this machine — by source ban,
source approval, or licence. A first detection asks instead of failing:
`resolve` prompts once per undecided finding and remembers each answer in a
machine-local store the audit then honours.

```sh
uv run --project tools/skill-trust skill-trust --config trust.yaml check owner/repo
uv run --project tools/skill-trust skill-trust --config trust.yaml audit --skills-dir ~/.agents/skills
uv run --project tools/skill-trust skill-trust resolve        # interactive, in a terminal
uv run --project tools/skill-trust skill-trust trust list     # every recorded decision
```

With no `--config`, commands read `~/.config/skill-trust/rules.yaml` when the
Ansible guard has written it — judging exactly as the guard would.

Exit codes match `bin/policy`, because this answers the same shape of question
and a caller should not have to learn two vocabularies:

| code | meaning |
|---|---|
| 0 | permitted |
| 1 | denied |
| 2 | unknown — nothing was examined, which is not the same as nothing wrong |
| 3 | error — the rules could not be read |
| 127 | a dependency is missing (`gh`, unless `--offline`) |

## Foreign buckets

A **foreign bucket** is a directory another program owns inside the skills
store — Claude Code's cloud sync writes `synced/<id>/`. `skill-trust` has no
jurisdiction over it, so it declines to rule rather than deny:

- A bucket is recognised by evidence, never by name: the path `synced/<id>/`, a
  sibling `.bucket-<id>` marker, and a `manifest.json` that parses to a
  `skills[]` array. All three must hold.
- A recognised bucket resolves to a recorded `external` verdict — a date and a
  reason — not a denial. `external` is "not mine to rule on", which is not
  "allowed"; the audit still exits permitted and prints the bucket.
- `deny` is refused against a foreign bucket. Deleting a synced skill only makes
  the sync recreate it byte-identical on the next session, so deny loops
  forever; the tool says so and names the inert rule rather than attempting it.
- Rules key on the bucket id, never the alias (`claude-sync`, or
  `claude-sync@<first8>` when several buckets exist). The alias is a display
  label, so renaming it cannot change what is approved.

`foreign_buckets: false` in the config turns this off and restores the previous
fail-closed denial.

## Precedence

Highest first, failing closed at the bottom:

1. **`foreign bucket`** — a directory another program owns is external; it never
   reaches the rules below.
2. **`deny_sources`** — a ban is a judgement about a publisher and outranks the
   paperwork. A denied source with an impeccable MIT licence is still denied.
3. **`deny_skills`** — a skill denied by name, whatever its source. This is how
   an interactive rejection persists: it keeps failing until the directory is
   removed.
4. **`exclude`** — a named skill vetoed from an otherwise approved source.
5. **`approved_sources`** — explicit allow; no licence lookup needed.
6. **`licence`** — permissive admits an unnamed source.
7. **deny.**

## The machine-local store

`~/.config/skill-trust/trust.yaml` holds decisions made interactively —
approvals, denials, vendored exceptions. It is never versioned: per-machine
decisions stay on the machine. Every entry carries a `why` and a `decided`
date, because a decision without a reason is a forgettable one.

The store layers **under** the `--config` rules. Decision lists union, with
deny always checked first — so a store denial tightens a repo approval, but a
store approval can never overturn a repo ban, and the store cannot touch
licence policy at all. An absent store reads as empty; a malformed one errors
with the file, kind and entry named. Edit it by hand, or with
`skill-trust trust add|list|remove`.

`resolve` is the interactive front: it audits, asks once per *undecided*
finding (vendor / deny / approve source / leave), saves each answer the
moment it is given — an interrupted run keeps what was answered — then
re-judges so you see the report the next guard run will produce. Recorded
denials are reported, never re-asked. Without a terminal it refuses and
points at `trust add`.

## Hidden directories

A dot-prefixed directory in the skills store is not a skill load path for any
loader that could be checked, so the audit skips it — this is what keeps a
trash directory like `.trash` from failing runs. Verified 2026-10-21:

| Loader | Hidden dirs skipped? | Evidence |
|---|---|---|
| dotagents (the manager) | yes, mechanically | `SKILL_NAME_RE` requires an alphanumeric first character; its sync names hidden dirs (including `.trash/`) as non-skills |
| opencode | yes | `skill-scan.ts` filters `entry.name.startsWith(".")` and ignores `**/.*` globs |
| codex | yes, host loader | `host.rs` prunes hidden directories (`HiddenDirectoryPolicy::Skip`); the executor-environment path includes them by design |
| claude-code, cursor, copilot | unverified | closed or minified builds |

A skip nobody can see is a place to hide something, so every skipped
directory is named in a `SKIPPED` line on every run, and `include_hidden`
(config or store) puts a named directory back under judgement.

## Licences

Three tiers, not a binary. Permissive auto-trusts. Copyleft is open but vendoring
into a library every agent loads is redistribution, so it needs
`licences.allow_copyleft`. Source-available — BUSL, SSPL, FSL, Elastic — is
**denied**: it reads like open source and is not.

**Absent is not permissive.** No LICENSE, or GitHub's `NOASSERTION`, means all
rights reserved — the most restrictive position there is, not the least.

Discovery runs most-specific-first: the skill's own frontmatter or `LICENSE`,
then the repository via `gh`. A permissively licensed skill can live inside a
differently licensed repository, and its own licence is the truth about it.
The repository lookup is only reached when no explicit rule already decided, so
an approved or banned source never touches the network.

## Config

```yaml
deny_sources: [some-org, other/repo]      # bare owner bans the whole org
deny_skills: [unwanted-skill]             # deny a skill directory by name
                                          # (a hidden dir needs include_hidden
                                          # too — the skip is checked first)
approved_sources: [bengineerdavis/ai-prompt-library, getsentry/skillet]
exclude:
  getsentry/skillet: [openspec-archive-change]
vendored: [no-ai-slop]                    # allowed to exist undeclared
include_hidden: [.gitmodules]             # audit this dot-dir after all
foreign_buckets: true                     # recognise a foreign bucket as external
licences:
  allow_copyleft: false
installed:                                # what declares what, for `audit`
  - {name: commit-hygiene, source: bengineerdavis/ai-prompt-library}
```

The store uses the same keys, with one difference: entries are mappings
carrying `why` and `decided` (bare strings are accepted on read):

```yaml
approved_sources:
  - source: owner/repo
    why: MIT, reviewed the repository
    decided: 2026-10-21
```

## Dependencies

One runtime dependency: `pyyaml>=6`. `uv.lock` is generated against **public
PyPI** so it stays portable — no private infrastructure belongs in a tracked
file. A machine that must pull from the private Sentry PyPI does so through its
machine-local uv configuration (`UV_INDEX_URL` or a global `uv.toml` entry),
never by committing the private index into `uv.lock` or `pyproject.toml`; a
lockfile re-generated against the private index must not be committed back.

## Graduating

Self-contained by design: nothing here imports from outside this directory, and
the tests live beside the code rather than in the repo's `tests/`. When it
outgrows the dotfiles repo, `git subtree split` on `tools/skill-trust/` yields a
repository that already builds and installs, rather than one needing a packaging
pass first. That is the difference between a tool you install and one you clone.
