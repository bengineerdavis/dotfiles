---
id: DOT-248
title: Make bash syntax the standing convention for .zsh files
status: To Do
created_date: 2026-10-28 01:23
labels:
- conventions
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Shellcheck already lints .zsh as shell, but docs/LANGUAGES.md calls that profile interim, shellharden is absent, and *.zsh.j2 templates escape linting. A zsh-only conditional in loreai-env.zsh.j2 silently dropped the service's OpenRouter key under dash on 2026-10-27.

Ship:

- Make bash syntax the standing rule for .zsh files in docs/LANGUAGES.md and AGENTS.md, with explicit inline disables for genuine zsh features.
- Add shellharden through mise and apply shellharden plus shellcheck across .zsh and .sh files, fixing violations.
- Add an .editorconfig only if it records shell indentation without conflicting with existing conventions.
- Queue a follow-up for rendered-output shell checks of *.sh.j2 and *.zsh.j2 templates.

Constraints:

- .zsh marks usage, not a separate language; do not add a separate zsh checker.
- Enforcement changes and fixes are branched work; hot files need the covering lease.
- Any new hook script is surfaced to the author under the build ladder before implementation.

Agreed with the maintainer 2026-10-27: use standard bash code in .zsh files and make deviations loud.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 docs/LANGUAGES.md and AGENTS.md state the standing bash-in-.zsh convention and explicit-disable rule.
- [ ] #2 shellharden is installed through mise and shellharden plus shellcheck pass over the repo's .zsh and .sh files.
- [ ] #3 Genuine zsh-only constructs carry inline shellcheck disables with reasons.
- [ ] #4 A follow-up task exists for rendered-output checks of shell templates.
- [ ] #5 uv run --frozen pytest tests/docs tests/hooks -q passes.
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
