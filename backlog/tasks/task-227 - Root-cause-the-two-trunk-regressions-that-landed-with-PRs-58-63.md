---
id: TASK-227
title: 'Root-cause the two trunk regressions that landed with PRs #58–63'
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Root-cause the two trunk regressions that landed with PRs #58–63.**
  [observed 2026-10-19 by the coordinator collecting payload-seam; both
  reproduced on pristine origin/main 92615ec in a scratch checkout] (a)
  tests/topics/test_opencode_config_layers.py:
  test_os_then_host_layers_override_common and
  test_ruling3_small_model_and_trivial_agents_render fail — opencode-layer
  rendering, likely from the oc2 work. (b) tests/topics/test_apt_source_audit.py:
  seven tests error at fixture setup with CalledProcessError — the fixture
  shells out to dotfiles/apps/apt/files/apt_keyring.py, which a PR in this
  range changed; the fixture and the script need reconciling. Note for the
  fixer: the pre-commit pyrefly hook checks project state and now excludes
  dotfiles/apps/opencode/molecule (merge de46484) because testinfra is
  group-scoped; check whether these failures share a root cause with that
  environment split. Done when both suites pass on main from a default
  environment (no extra groups) or each failure has a named owner and an
  open PR. [unclaimed]
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
