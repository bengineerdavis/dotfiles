# `skill-trust`

Decides whether an agent skill may be installed on this machine — by source ban,
source approval, or licence.

```sh
uv run --project tools/skill-trust skill-trust --config trust.yaml check owner/repo
uv run --project tools/skill-trust skill-trust --config trust.yaml audit --skills-dir ~/.agents/skills
```

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
3. **`exclude`** — a named skill vetoed from an otherwise approved source.
4. **`approved_sources`** — explicit allow; no licence lookup needed.
5. **`licence`** — permissive admits an unnamed source.
6. **deny.**

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
approved_sources: [bengineerdavis/ai-prompt-library, getsentry/skillet]
exclude:
  getsentry/skillet: [openspec-archive-change]
vendored: [no-ai-slop]                    # allowed to exist undeclared
foreign_buckets: true                     # recognise a foreign bucket as external
licences:
  allow_copyleft: false
installed:                                # what declares what, for `audit`
  - {name: commit-hygiene, source: bengineerdavis/ai-prompt-library}
```

## Graduating

Self-contained by design: nothing here imports from outside this directory, and
the tests live beside the code rather than in the repo's `tests/`. When it
outgrows the dotfiles repo, `git subtree split` on `tools/skill-trust/` yields a
repository that already builds and installs, rather than one needing a packaging
pass first. That is the difference between a tool you install and one you clone.
