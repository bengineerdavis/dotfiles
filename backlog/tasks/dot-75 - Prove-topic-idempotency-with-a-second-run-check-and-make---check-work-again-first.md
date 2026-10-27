---
id: DOT-75
title: Prove topic idempotency with a second-run check, and make `--check` work again
  first
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Prove topic idempotency with a second-run check, and make `--check` work
  again first.** Measured 2026-09-14 by dry-running
  `--tags "upgrade,install,minimal"`: `ok=104 changed=6 failed=1`. The good
  news is that **no package install task reported changed** — `state: present`
  converges as advertised, so adding `install` to `./update`'s tags would add
  missing topics without reinstalling present ones. The six that did change:
  two are the homebrew upgrade tasks doing their job; `apps/ollama` "Download
  latest Ollama Zsh completion to temporary path" fetches to a fresh tempfile
  every run and so reports changed forever; and three script/agent installs
  (`ollama` launchd agent, `clamav` daily script, `lynis` monthly script) need
  checking for real drift versus a check-mode artifact. The blocker is
  `failed=1`: `roles/guards/tasks/dotagents-approved-sources.yaml:59` dies under
  `--check` because the `tempfile` task above it is skipped, leaving
  `guard_trust_config` a dict with no `.path` — so the repo cannot currently be
  dry-run at all. `check_mode: false` is the fix and the repo already uses it
  four times (`apps/homebrew/tasks/upgrade.yaml:19` is the precedent). The
  standard for the test itself is molecule's `idempotence` action — run converge
  twice, fail if the second reports changed — which needs no molecule adoption
  to copy. Done when `--check` completes clean across all topics, a second
  consecutive real run reports `changed=0`, and the check runs per topic so a
  failure names which one. Pairs with the per-topic suite task below.
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
