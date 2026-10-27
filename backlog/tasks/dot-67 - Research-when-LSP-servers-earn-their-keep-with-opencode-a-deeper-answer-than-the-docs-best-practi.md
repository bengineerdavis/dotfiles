---
id: DOT-67
title: Research when LSP servers earn their keep with opencode — a deeper answer than
  the docs' best-practi
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Research when LSP servers earn their keep with opencode — a deeper
  answer than the docs' best-practices page gives.** High priority, queued
  by the author 2026-09-15. The page (https://opencode.ai/docs/lsp/, fetched
  2026-09-15) says LSP is disabled by default, lists 30+ built-in servers
  that auto-start on matching extensions, and concludes that lint/typecheck
  CLIs documented in AGENTS.md or skills often beat language-server
  feedback. That is the hypothesis to test, not to accept. The research must
  settle: per-language payoff (pyright wants a project dep, several
  auto-install, `OPENCODE_DISABLE_LSP_DOWNLOAD` gates downloads); the real
  cost terms (memory, version skew, out-of-sync servers) weighed against
  agent-loop value; where `lsp` config should live per repo and per topic
  here; and which repos actually earn enablement. Route it as a
  review-best-practices pass — what exists, what practitioners do, ranked
  options with rejections recorded — and it feeds the llocallabs topic
  design. Done when a written recommendation says when LSP earns its keep
  here, per language, and the author has made the adopt/adapt/reject call.
  [me]
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
