# LANGUAGES.md

What languages this repository is written in, and the reusable tool profile
that goes with each. The inventory is here so reuse across languages and
projects is explicit rather than by memory. Python detail lives in
`docs/PYTHON.md`; this file points at it rather than repeats it.

## Where the languages are

| Directory | Languages |
|---|---|
| `bin/` (chezmoi source; deploys to `~/bin`) | bash; Python, both stdlib and PEP 723 (`#!/usr/bin/env -S uv run --script`) |
| `scripts/` | bash (`run-bats.sh`), Python (`check_commit_proportionality.py`), zsh (`chezmoi_symlink_config.zsh`) |
| `tools/skill-trust/` | Python (uv tool project) |
| `tests/` | Python (pytest) and bash (bats) |
| `dotfiles/apps/*/tasks/`, `dotfiles/playbook.yaml` | YAML + Jinja2 (Ansible) |
| `dot_config/` | zsh, and chezmoi `*.tmpl` templates (Go template syntax) |

The bash-versus-Python choice is `AGENTS.md` § Languages; the Python toolchain
is `docs/PYTHON.md`.

## Reusable profiles

One row per language: the tools that go with it, so a profile can be lifted
for another project. **Installed** means wired into the documented workflow;
**queued** means a `TASKS.md` item owns it; **TBD** means the choice is still
open.

| Language | Formatter | Linter | Typecheck | Test | LSP |
|---|---|---|---|---|---|
| Python | ruff (enforced on commit) | ruff (enforced on commit) | pyrefly 1.3.2 (enforced on commit) | pytest + hypothesis; xdoctest (queued) | pyrefly (editor wiring queued) |
| bash | — | shellcheck | — | bats | bash-language-server (TBD) |
| zsh | — | shellcheck (bash standard, interim) | — | — | — |
| YAML / Ansible | — | — | — | molecule (queued) | yaml-ls (TBD) |

Notes:

- **LSP is undecided by design.** Which server, and whether the profile lives in
  the chezmoi global template (all projects) or a per-repo `opencode.jsonc`, is
  the open question owned by the queued "Configure opencode LSP profiles" task in
  `TASKS.md`. This file records the candidates; it does not wire them. Until that
  task lands, opencode has no `lsp` section and LSP is off.
- **ruff and pyrefly enforce on commit** (ruff-check, ruff-format and
  pyrefly-check hooks). The doc-line rules ruff selects carry per-path
  grandfathers while the docstring campaign runs; pyrefly carries a 69-comment
  suppress baseline that shrinks over time.
  See `docs/PYTHON.md`.
- **`.zsh` marks how a file is used, not a different language.** These files are
  zsh lifecycle fragments sourced into the shell config; the extension says where
  the file fits, not that it needs its own toolchain. The bash standard is the
  interim profile: the pre-commit shellcheck hook runs on every `types: [shell]`
  file, and identify tags `.zsh` as `shell`, so fragments are already linted as
  shell. Trusting that output on zsh is the author's working position, pending
  the queued zsh-tooling research (`TASKS.md`), which owns whether the bash
  standard is kept, adapted, or replaced.
- **This table is a tracking doc, not config.** Promoting a row into global or
  per-project config is a per-entry decision made when a tool is actually wired.
  The LSP row is the first candidate, and its home is the queued task's to settle.
