---
id: DOT-90
title: Integrate `xdoctest` and make illustrative examples a tested part of the
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Integrate `xdoctest` and make illustrative examples a tested part of the
  docs. Docstring examples in the 22 Python scripts and any Python modules
  run under pytest via the xdoctest plugin; docs (`dotfiles/docs/`, READMEs)
  carry code examples where they clarify, verified rather than trusted —
  written for humans first, machines as the proof they still work. Survey the
  ecosystem before building anything: xdoctest for docstrings, and for fenced
  blocks in markdown weigh sybil / pytest-examples / a pytest-markdown runner
  before hand-rolling one. Done when: xdoctest is in the documented pytest
  command (AGENTS.md § Commands), docstring examples in `bin/` are collected
  and green, `docs/PYTHON.md` records the convention (what must carry
  examples, how to write and run them), and a markdown-example mechanism is
  either adopted or consciously rejected with the reason recorded. Pairs
  with the plain-language standard item — examples are prose too.
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
