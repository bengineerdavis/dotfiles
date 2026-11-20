---
id: DOT-402
title: Make agent-tooling topics detect a missing CLI rather than requiring it
status: To Do
created_date: 2026-11-20 18:29
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

**Why.** `apps/claude-code` installs a zsh fragment that defines `claude` and
`claude-lore` wrappers, but nothing in the repo installs the `claude` binary
itself. Any surface built on it — the profile tests, and anything that shells
out to an agent CLI — therefore fails on a machine without that CLI, and fails
as a test failure rather than as "this host does not have the tool".

Measured 2026-11-20: `tests/claude_credentials` passes on this machine (where
`/opt/homebrew/bin/claude` exists) and fails in CI. That difference is
host state, not a code defect, which is why it sits in the CI baseline instead
of being fixed.

**Ship**

- Decide, per agent-CLI topic, whether the tool is a hard requirement of the
  topic or an optional integration; record the answer in the topic's README.
- Where it is optional, make the topic detect an absent CLI and say so
  plainly instead of failing obscurely — the same fail-closed-with-a-named-fix
  shape `require()` uses in `home/bin/llm-ctx`.
- Make the dependent tests skip (or assert the documented absence) when the CLI
  is missing, so a host without it reports *why* rather than a red suite.
- State plainly which topics own installing an agent CLI and which only
  configure one that is already present.

**Constraints**

- Do not install an agent CLI as a side effect of a topic that only configures
  one; that is a scope decision for the author.
- A skip must name what is missing and how to install it. A silent skip is the
  defect this task exists to remove — the `.lore.md` and `pyyaml` notes in
  AGENTS.md are the same class.
- Keep the CI baseline honest: removing a failure from the baseline is only
  correct if the failure is genuinely gone, not merely skipped.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 Each agent-CLI topic states whether the CLI is required or optional
- [ ] #2 A host without the CLI gets a named, actionable message rather than an obscure failure
- [ ] #3 Dependent tests skip with a reason naming the missing tool, or pass legitimately
- [ ] #4 No topic installs an agent CLI that it previously only configured

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
