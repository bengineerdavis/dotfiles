# REFERENCES.md

External standards this repository follows, the version it follows, and when
that was last checked against the source.

A convention with no version silently means whatever its latest revision says.
That is drift which produces no diff and no failing test — the reason this file
exists.

**Last full review: 2026-09-11.** Cadence: re-check on any quarter boundary, and
whenever a row's tooling is upgraded. Update `verified` when you look, even if
nothing changed — a stale date is the signal, not the version number.

## Followed

| Standard | Version followed | Where it binds | Verified |
|---|---|---|---|
| [AGENTS.md](https://agents.md/) | unversioned convention | `AGENTS.md` at root | 2026-09-11 |
| [Inline script metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/) (PyPA) | living spec; post-Jan-2024 form | 36 scripts in `bin/` and topic `files/` | 2026-09-11 |
| [PEP 723](https://peps.python.org/pep-0723/) | approval record only — **not** the current spec | historical; cite PyPA instead | 2026-09-11 |
| [PEP 508](https://peps.python.org/pep-0508/) — dependency specifiers | Final | the `dependencies` list inside PEP 723 blocks | 2026-09-11 (via 723) |
| [skillet](https://www.npmjs.com/package/@sentry/skillet) | **1.7.0** pinned in `spec.md` footer | `spec.md`, every skill spec | 2026-09-11 |
| [copier](https://copier.readthedocs.io/) | 9.17.2 installed | planned templates; no inheritance, composition only | 2026-09-11 |
| [GitHub community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors) | current docs | `CONTRIBUTING.md` placement | 2026-09-11 |
| [no-ai-slop](https://github.com/petergyang/no-ai-slop) | vendored MIT @ 2026-09-02 | `~/.claude/skills/no-ai-slop/` | 2026-09-11 |
| [shellcheck-py](https://github.com/shellcheck-py/shellcheck-py) | `v0.10.0.1` in `.pre-commit-config.yaml` | pre-commit hook | 2026-09-11 |
| [prek](https://github.com/j178/prek) | 0.5.0 | hook runner; writes `.git/hooks/` | 2026-09-11 |
| [scriv](https://scriv.readthedocs.io/) | run via `uv run --with scriv` | `changelog.d/` fragments → `CHANGELOG.md` | 2026-09-11 |
| [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) | **1.1.0** | category names in `changelog.d/scriv.ini` | 2026-09-11 |
| [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606) — reserved example names | Best Current Practice | synthetic PII fixtures use `example.com`/`.org` | 2026-09-11 |

### Why PyPA and not the PEP

A PEP records a decision at a moment; the PyPA specification is the living
document and it moves. Inline script metadata changed **after** PEP 723 was
accepted — in January 2024 the block type was renamed from `pyproject` to
`script` and the `[run]` table was dropped, lifting `dependencies` and
`requires-python` to the top level.

Our scripts use the post-amendment form, so they are current. But a reader
sent to the PEP could implement the superseded shape and be correct according
to the document they were given. Cite the living spec; keep the PEP as the
provenance of the decision.

The same test applies to any standard here: if it has a living home and an
approval record, the register points at the living home.

### Watch list

- **skillet 1.8.0 is available** and `spec.md` pins 1.7.0. Upgrading changes what
  `skillet validate` accepts, so read its changes before moving the pin.
- **ruff 0.16.5 is installed but wired to nothing.** When it is wired, pin the
  ruleset here — PEP 723's `[tool]` table lets ruff config live in each script,
  which may remove the need for a repo-wide config file.

## Deliberately not followed

Recorded so the decision is not re-litigated. Each was measured, not assumed.

| Standard | Why not |
|---|---|
| [Conventional Commits](https://www.conventionalcommits.org/) | 12% of history uses it; 71% uses a plain `<scope>: ` prefix. Its payoff is automated changelog generation and semver; this repo writes changelog entries by hand with scriv and does not release. |

| [Semantic Versioning](https://semver.org/) | Nothing here is released or consumed as a version. |
| [Contributor Covenant](https://www.contributor-covenant.org/) | `PRD.md` § Non-goals: not expecting contributors. |
| cursor's `unslop` | Its "avoid em dashes entirely" conflicts with measured house style (12 per 1000 words in documents predating any agent). `no-ai-slop` reaches the same goal with a calibrated rule. |
| commitlint / gitlint / commitizen | They enforce format; format is already 71% consistent. The measured defect was length, which none of them check. |

## Undecided

- **Plain-language standard.** `spec.md` and `AGENTS.md` require plain language
  and describe it, but cite no published standard.
  [plainlanguage.gov](https://www.plainlanguage.gov/guidelines/) and
  [ISO 24495-1:2023](https://www.iso.org/standard/78907.html) are the candidates.
  Open in `TASKS.md`.


## How to re-check

There is no automation. Open each link, compare the version column, and update
`verified` whether or not anything moved. Where a tool is installed locally,
`--version` is the faster check:

```bash
skillet --version; copier --version; prek --version; ruff --version
grep -o 'skillet-version: [0-9.]*' spec.md
grep -A1 shellcheck-py .pre-commit-config.yaml | grep rev
```
