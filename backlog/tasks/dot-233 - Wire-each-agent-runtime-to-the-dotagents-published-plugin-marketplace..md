---
id: DOT-233
title: Wire each agent runtime to the dotagents-published plugin marketplace.
status: To Do
created_date: 2026-10-27 19:41
labels:
- dotagents
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wire each agent runtime to the dotagents-published plugin marketplace.

**Why:** dotagents publishes plugin marketplaces under ~/.agents/plugins (marketplace.json with the dotagents-managed marker; mattpocock-skills clone with skills/{deprecated,engineering,in-progress,misc,productivity}), but links plugin skills into ~/.config/opencode/skills only — e.g. ask-matt -> ../../../.agents/plugins/mattpocock-skills/skills/engineering/ask-matt. Store-skill wiring exists for the other runtimes: ~/.claude/skills and ~/.copilot/skills are symlinks to ~/.agents/skills, while ~/.cursor/skills and ~/.codex/skills hold real entries with no links. So plugin-sourced skills (mattpocock/skills) load in opencode only; claude, cursor, codex, copilot and vscode get nothing from the plugin marketplace. Measured 2026-10-27. ~/.claude/plugins already carries a native marketplace registry (claude-plugins-official), which may offer a native wiring path for claude.

**Ship:** every runtime declared in apps/dotagents defaults/main.yaml (dotagents_agents) reaches plugin-sourced skills through a defined mechanism — native plugin registration where the client supports it (claude), skill-dir links where it does not — or a recorded per-runtime exclusion with a reason. The wiring lives in the apps/dotagents topic (defaults/config), not in hand-created links; if the pinned binary cannot do it, the gap is filed upstream or resolved by pinning a newer dotagents through the topic.

**Constraints:** owned by apps/dotagents — no per-agent topics are created for this; runtimes are already declared in the topic's dotagents_agents. Do not modify ~/.agents/skills content (provenance-audit scope). The dotagents binary version follows the mise pin (3.3.0 today); a capability gap is handled by a pin bump through the topic or an upstream request, never ad-hoc installs. Wiring must be idempotent and re-runnable through the topic playbook.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every runtime in dotagents_agents reaches plugin-sourced skills (mattpocock/skills) through a defined mechanism, or carries a recorded exclusion with reason; verification: for each agent dir, a link into ~/.agents/plugins or a native plugin registration exists (or its exclusion is in the topic CHANGELOG).
- [ ] #2 The wiring mechanism is declared in apps/dotagents (defaults/main.yaml or topic config), not hand-created links; verification: grep -r mattpocock apps/dotagents shows the mechanism.
- [ ] #3 ~/.agents/skills content is unchanged by the wiring (provenance audit still passes); verification: uv run --frozen pytest tests/docs tests/hooks -q passes.
- [ ] #4 The dotagents CHANGELOG known_issues entry "Plugin skills reach opencode only" is closed or amended to describe what ships; verification: CHANGELOG.md matches the shipped mechanism.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Machine measurement 2026-10-27: opencode wired (ask-matt, chief-of-staff, claude-handoff etc. -> ../../.agents/plugins/mattpocock-skills/...); claude and copilot store-linked (~/.claude/skills -> ../.agents/skills, ~/.copilot/skills -> ../.agents/skills, no plugin links); cursor and codex hold 11 real entries each, zero links; vscode has no skills dir. dotagents binary 3.3.0 (mise pin), 3.4.0 available. mattpocock/skills approved 2026-10-26 (MIT, gh api verified).
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
