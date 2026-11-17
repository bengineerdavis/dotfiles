---
id: DOT-371
title: Pin the pipx:ansible venv to a Python 3.15-compatible interpreter
status: To Do
created_date: 2026-11-17 17:20
labels:
- bug
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Why: ansible-playbook red on this machine 2026-11-17 — the pipx:ansible venv rebuilt on Python 3.15.2 (2026-11-16 16:01) after the deployed mise config's python line moved 3.14→3.15 at 16:00, and ansible-core 2.21.6 (pinned by the ansible 14.6.0 meta-package ~=2.21.6) patches dataclasses._is_type, which 3.15 removed (ansible/ansible#87677; fixed in 2.22.0 which the meta-package pin cannot reach).

Ship:
- Deployed ~/.config/mise/config.toml: pipx:ansible uvx_args carries --python 3.14 (applied 2026-11-17, verified: ansible-playbook --version green, venv pyvenv.cfg says 3.14.8).
- Source home/dotfiles/apps/mise/files/config.toml: same --python 3.14 line, so a future chezmoi apply cannot revert the pin.
- Acceptance: mise exec -- ansible-playbook --version exits 0 with core 2.21.6 on python 3.14; run-role.sh opencode completes on the deployed fix.

Constraints:
- The pin is per-tool (uvx_args), not a global python revert — python = "3.15" stays unless separately decided.
- Source change lands by PR per house rules (deployed-tree payload).
- Note the open question: who wrote python = "3.15" into the deployed config at 2026-11-16 16:00 — user, update.sh, or mise — and confirm intent before a chezmoi apply could overwrite it back to 3.14.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 mise exec -- ansible-playbook --version exits 0
- [ ] #2 pyvenv.cfg of the pipx:ansible venv reports 3.14
- [ ] #3 source config.toml carries the --python 3.14 uvx_args line
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
