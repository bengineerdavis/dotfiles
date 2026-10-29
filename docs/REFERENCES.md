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
| [AGENTS.md](https://agents.md/) | unversioned convention; stewarded by the Agentic AI Foundation (Linux Foundation) since 2026 | `AGENTS.md` at root | 2026-09-12 |
| [Agent Skills specification](https://agentskills.io) | current spec; format only — no distribution | every `SKILL.md`; see `docs/AGENT-ARTIFACTS.md` | 2026-09-12 |
| [dotagents](https://github.com/getsentry/dotagents) (@sentry/dotagents) | 3.1.0 installed; MIT | skill distribution; `agents.toml` + `agents.lock` under `~/.agents/` | 2026-09-12 |
| [Inline script metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/) (PyPA) | living spec; post-Jan-2024 form | 22 Python scripts in `home/bin/` and topic `files/` | 2026-09-23 |
| [PEP 723](https://peps.python.org/pep-0723/) | approval record only — **not** the current spec | historical; cite PyPA instead | 2026-09-11 |
| [PEP 508](https://peps.python.org/pep-0508/) — dependency specifiers | Final | the `dependencies` list inside PEP 723 blocks | 2026-09-11 (via 723) |
| [skillet](https://www.npmjs.com/package/@sentry/skillet) | **1.7.0** pinned in `spec.md` footer | `spec.md`, every skill spec | 2026-09-11 |
| [Ansible collections](https://docs.ansible.com/ansible/latest/galaxy/user_guide.html) (`community.general`, `community.docker`) | **13.0.1 / 5.2.1** exact-pinned in `home/dotfiles/requirements.yml` (O1, 2026-09-19) | every topic task invoking `community.general.*` / docker; the support-grade records pin to these | 2026-09-19 |
| [copier](https://copier.readthedocs.io/) | 9.17.2 installed | planned templates; no inheritance, composition only | 2026-09-11 |
| [mise Python cookbook](https://mise.jdx.dev/mise-cookbook/python.html) | living docs | the uv ↔ mise split (`mise sync python --uv`, `python.uv_venv_auto`); **we deviate** — uv is astral-installed at the system level, not `[tools] uv = "latest"`, so `mise upgrade` never churns the uvx that builds `pipx:ansible` | 2026-09-28 |
| [GitHub community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors) | current docs | `CONTRIBUTING.md` placement | 2026-09-11 |
| [no-ai-slop](https://github.com/petergyang/no-ai-slop) | vendored MIT @ 2026-09-02 | `~/.claude/skills/no-ai-slop/` | 2026-09-11 |
| [shellcheck-py](https://github.com/shellcheck-py/shellcheck-py) | `v0.10.0.1` in `.pre-commit-config.yaml` | pre-commit hook | 2026-09-11 |
| [prek](https://github.com/j178/prek) | 0.5.0 | hook runner; writes `.git/hooks/` | 2026-09-11 |
| [Lychee](https://github.com/lycheeverse/lychee) | **0.24.2** through `aqua:lycheeverse/lychee` | local documentation links in pre-commit; reviewed external checks via `scripts/check-docs-links.py` | 2026-10-29 |
| [scriv](https://scriv.readthedocs.io/) | **1.8.0** pinned in the merge workflow; run locally via `uv run --with scriv` | `changelog.d/` fragments → `CHANGELOG.md` after each merged PR; no semantic versions or GitHub Releases | 2026-10-28 |
| [backlog-md-py](https://github.com/rmusser01/backlog-md-py) 2.2.0 | pipx via mise (`pipx:backlog-md-py`) | the task queue: `backlog/` at repo root, `backlog-py --cwd .` — Python compatibility clone of Backlog.md | 2026-10-23 |
| [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) | **1.1.0** | category names in `changelog.d/scriv.ini` | 2026-09-11 |
| [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606) — reserved example names | Best Current Practice | synthetic PII fixtures use `example.com`/`.org` | 2026-09-11 |
| [Trunk Based Development](https://trunkbaseddevelopment.com/) (Hammant) | living site | short-lived branches, merge often — already practice; codified by the ground-shift protocol (`docs/research/coordinating-parallel-work-across-refactors.md`) | 2026-10-04 |
| [Branch by Abstraction](https://martinfowler.com/bliki/BranchByAbstraction.html) (Fowler) | living article | the layout seam (`PAYLOAD_ROOT`) consumers go through during structural shifts | 2026-10-04 |

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

- **MCP** ([modelcontextprotocol.io](https://modelcontextprotocol.io)) —
  specification 2026-07-28 verified 2026-09-12. Adopted as the tool-execution
  *boundary* (target state, nothing stood up) — see
  `docs/MODEL-ACCESS.md`. Track SEP-1024 (client security for local
  installs) and the Skills Over MCP working group.
- **LiteLLM** ([github.com/BerriAI/litellm](https://github.com/BerriAI/litellm))
  — verified 2026-09-12. Deferred with a named trigger: revisit when model
  access becomes multi-developer, gated on employer permission and on what
  the MIT core covers versus the enterprise tier. The incumbent (`llm` +
  provider plugins) holds until then because the egress policy resolver wraps
  it and no gateway does.
- **A2A** ([a2a-protocol.org](https://a2a-protocol.org/), Linux Foundation,
  contributed by Google) and **ACP**
  ([agentclientprotocol.com](https://agentclientprotocol.com)) —
  agent-to-agent and editor-to-agent interop protocols. Tracked, not
  followed; adjacent to model access and artifact management, no current use
  on this machine.
- **Agent Plugins v1** ([agent-plugins.org](https://agent-plugins.org)) — the
  bundle format dotagents implements for plugins; relevant when plugin scope
  opens.
- **skills.sh** ([vercel-labs/skills](https://github.com/vercel-labs/skills)) —
  used for discovery only. Its CLI telemetry is on by default
  (`DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1` to disable); it cannot pin or
  lock, which is why it is not the installer.
- **skillet 1.8.0 is available** and `spec.md` pins 1.7.0. Upgrading changes what
  `skillet validate` accepts, so read its changes before moving the pin.
  **Update 2026-09-15: the read is done and the premise was wrong.** The pin
  moved to 1.8.0 in `config.toml` on local evidence while the read was
  believed blocked; it was not — `gh api` reaches getsentry/skillet from the
  Mac (the block was the other machine's). The 1.7.0→1.8.0 compare (5
  commits, github.com/getsentry/skillet/compare/1.7.0...1.8.0) shows the
  grammar and exit-code logic UNTOUCHED — acceptance is identical; what
  changed is diagnostics (the "Behavior has no eval case" warning was
  deleted; the coverage section renamed) and the authoring workflow
  (evals are opt-in — the `!` is `skillet new`/`status`, not `validate`).
  So this row's "changes what validate accepts" was inaccurate; the spec
  footer moves to 1.8.0 on this evidence.
- **ruff 0.16.5 is installed but wired to nothing.** When it is wired, pin the
  ruleset here — PEP 723's `[tool]` table lets ruff config live in each script,
  which may remove the need for a repo-wide config file.

## Deliberately not followed

Recorded so the decision is not re-litigated. Each was measured, not assumed.

| Standard | Why not |
|---|---|
| [Conventional Commits](https://www.conventionalcommits.org/) | 12% of history uses it; 71% uses a plain `<scope>: ` prefix. Scriv aggregates handwritten fragments after each merged PR; it does not infer changelog content or semantic versions from commit types. |
| [Semantic Versioning](https://semver.org/) | Nothing here is released or consumed as a version. |
| [Contributor Covenant](https://www.contributor-covenant.org/) | `PRD.md` § Non-goals: not expecting contributors. |
| cursor's `unslop` | Its "avoid em dashes entirely" conflicts with measured house style (12 per 1000 words in documents predating any agent). `no-ai-slop` reaches the same goal with a calibrated rule. |
| commitlint / gitlint / commitizen | They enforce format; format is already 71% consistent. The measured defect was length, which none of them check. |
| [Vercel AI Gateway](https://vercel.com/docs/ai-gateway) | A managed third-party control plane replaces the on-device egress policy decision and routes every model call through Vercel. Verified 2026-09-12 — see `docs/MODEL-ACCESS.md`. |
| Native vendor SDKs (Anthropic/OpenAI) as the model layer | The lock-in the anti-lock-in work exists to prevent. Hosted models arrive via OpenRouter through `llm`, local models through `llm-ollama`, behind one interface. |

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
