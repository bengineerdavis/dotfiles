---
id: TASK-19
title: Configure opencode LSP profiles for Python and Bash projects — ty or
status: To Do
created_date: 2026-10-23 16:49
labels:
- migration
ordinal: 17
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
pyrefly alongside ruff and the other servers that matter — if we are not
  doing that already.** Queued by the author 2026-09-15; the concrete
  follow-on to the research task directly above — that one settles WHEN
  LSP earns its keep with opencode, this one settles WHICH servers for
  Python/Bash and wires them. Verified 2026-09-15: we are not doing it
  already — neither `dot_config/opencode/opencode.jsonc.tmpl` nor the
  project `opencode.json` has an `lsp` section (rg finds none), so LSP is
  disabled-by-omission; ruff is mise-managed (`ruff = "latest"`) but wired
  to nothing per docs/REFERENCES.md; `ty` and `pyrefly` are both absent
  from the mise config (a § Later task queues installing `ty`); bash
  linting today is shellcheck in pre-commit. The docs
  (https://opencode.ai/docs/lsp/, fetched 2026-09-15) say `lsp: true`
  enables all 30+ built-ins and the object form configures per-server
  `command`/`extensions`/`disabled`/`env`/`initialization`; built-ins
  relevant here: pyright (.py, wants a project dep), bash (auto-installs
  bash-language-server), yaml-ls (auto-installs);
  `OPENCODE_DISABLE_LSP_DOWNLOAD=true` gates the auto-downloads. The work:
  decide ty vs pyrefly — pick one, not both (ty is pre-1.0 but the house
  toolchain names it; the queued install task owns the install, this owns
  the LSP wiring); decide where the profile lives — the chezmoi-managed
  global template (all projects, effective on apply + restart) versus
  per-repo `opencode.json`; and decide whether server downloads are
  permitted given bash-language-server and yaml-ls auto-install. Done when
  the chosen servers are configured in the chosen location, an opencode
  session on this repo shows Python and Bash server feedback, and the
  download policy is recorded. [me]

  Update 2026-10-03: part of this is done. Python's servers are wired in
  the repo-scoped `opencode.jsonc` — pyrefly in ba0bb90, ruff added the
  same day ("add ruff lsp to this project", author-directed), pyright
  disabled, pinned by
  `tests/permissions/test_opencode_tiers.py::test_lsp_pins_the_python_servers`.
  The global-vs-repo home decision, the ty-vs-pyrefly global call (this
  repo has effectively chosen pyrefly), the bash/yaml server wiring and
  the download policy are still this task's. The stale 2026-09-15
  verification above no longer holds.

Legacy: TASKS.md § Now item 17 of 49, migrated to backlog 2026-10-23 (branch agent/backlog-migration).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
