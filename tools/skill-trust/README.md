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

## Precedence

Highest first, failing closed at the bottom:

1. **`deny_sources`** — a ban is a judgement about a publisher and outranks the
   paperwork. A denied source with an impeccable MIT licence is still denied.
2. **`exclude`** — a named skill vetoed from an otherwise approved source.
3. **`approved_sources`** — explicit allow; no licence lookup needed.
4. **licence** — permissive admits an unnamed source.
5. **deny.**

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
licences:
  allow_copyleft: false
installed:                                # what declares what, for `audit`
  - {name: commit-hygiene, source: bengineerdavis/ai-prompt-library}
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
