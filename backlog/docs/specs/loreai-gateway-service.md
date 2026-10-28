---
type: spec
tags:
- ready-for-agent
id: DOC-2
title: 'Lore gateway: an always-on per-user service on macOS and Linux'
---

## Problem Statement

Agents route through a local Lore gateway, but nothing on either machine keeps that gateway alive. After a reboot — or any session that never started one — `lore doctor` fails with "no gateway responding", and every agent depending on it (claude-code, codex, and opencode via `lore run`) silently routes nowhere until a human runs `lore start --bg` by hand. The failure is worst on the Linux machine, where the topic's service half is render-verified only, and the bootstrapped service has already been observed installed-but-not-loaded on macOS after an apply/reboot cycle. A second, compounding break: the opencode plugin no longer loads on opencode 2.x (V1 plugin API), so even with a live gateway, opencode needs the `lore run opencode` interim and loses the plugin's in-session effects.

## Solution

The loreai topic owns a per-user service that starts the gateway at login and keeps it alive: a LaunchAgent on macOS, a systemd user unit on Linux. The gateway is simply always there — `lore doctor` stays green across reboots, the service manager restarts a dead gateway within seconds, and removing the topic tears the service down cleanly without harming the memory database. While the plugin is V2-incompatible, `lore run opencode` is the documented interim for routing opencode sessions through the gateway.

## User Stories

1. As a developer on the Linux machine, I want the gateway started at login by a systemd user unit, so my agent sessions never fail with "no gateway responding" after a reboot.
2. As a developer on the Mac, I want the gateway started at login by a LaunchAgent, so the same guarantee holds on both platforms.
3. As a developer, I want the unit to run the gateway in the foreground under the service manager, so the manager owns the lifecycle and respawns it if it dies.
4. As a developer, I want a hand-started gateway (`lore start --bg`) adopted rather than double-started on topic re-apply, so my running session is never disturbed.
5. As an operator, I want the enable-linger decision reported to me, never made for me, so session-less boot behavior on Linux stays my call.
6. As a developer, I want the health check to read the running gateway's own port file rather than assuming the default port, so a healthy gateway on a non-default port never false-fails the check.
7. As a developer, I want a crashed gateway back within seconds without my intervention, so transient crashes don't break agent routing.
8. As a developer re-applying the topic, I want the bootstrap to be idempotent (bootout → bootstrap → enable), so re-applies never stack duplicate services.
9. As a developer, I want the service import ordered after the env file exists and before agents are pointed at the gateway, so agent configs never reference an endpoint that isn't up yet.
10. As a developer on a fresh machine, I want the first apply to bring the gateway up cleanly, so there is no first-run ordering hazard.
11. As a developer removing the topic, I want teardown to stop the service and delete the unit before agent setups are undone, so no half-alive listener survives.
12. As a developer removing the topic, I want hand-launched gateways killed too, so no orphan listener survives teardown.
13. As a developer removing the topic, I want the memory database preserved, so teardown costs me nothing I care about.
14. As an opencode user, while the plugin is V2-incompatible, I want the `lore run opencode` interim documented, so I keep gateway routing and attribution despite the plugin break.
15. As an agent reviewing the service PR, I want Molecule integration tests on both macOS and Linux exercising this spec's edge cases in the branch, so the service behavior is proven per-platform before merge, not on my machines.
16. As a maintainer, I want every topic to carry Molecule scenarios covering the edge cases its spec names, so platform drift is caught in the branch that introduces it.
17. As a maintainer, I want the "installed but not loaded" persistence gap (observed on macOS) covered by a reboot scenario, so the bootstrap/enable claim is actually proven.
18. As an operator running `lore doctor` at any time, I want it to report the service's true state, so I can trust green.
19. As a developer, I want the unit to source the same env file as my interactive setup, so the gateway sees the worker model and provider key identically in both contexts.
20. As an agent on a spec-driven flow, I want tickets cut from this spec to inherit its edge-case list as their acceptance criteria, so nothing verified here is lost between spec and task.

## Implementation Decisions

- Per-user service only, never system-wide: a LaunchAgent plist on Darwin bootstrapped into the gui domain; a systemd user unit on Debian enabled and restarted. Both platforms keep the topic's report-never-change stance for operator decisions (enable-linger on Debian).
- Units run `lore start` in the foreground (no --bg) so the service manager owns the lifecycle; both source the topic's env file (worker model, provider key) that the prompts step writes on first install.
- Service import order: after the env file exists, before agents are pointed at the gateway.
- The health check reads the running gateway's own port file instead of assuming the default port, because `lore start` against an existing gateway is a no-op that reports the existing instance — adoption is by design, and a port-pinned doctor would false-fail.
- Teardown order in remove: stop the service, remove unit files and logs, kill hand-launched gateways, undo agent setups, remove the binary — the memory database is preserved.
- Interim routing: `lore run opencode` is confirmed working while the plugin is V2-incompatible; plugin-side effects (auto-compaction disable, per-project memory files) remain off until the routing decision lands. The decision (local shim vs. wait upstream vs. chezmoi partial config) is the author's; this spec records the interim, not the choice.

## Testing Decisions

- **Molecule integration tests are required, in the branch, before merge** — and this is the standing rule for every topic: each spec's edge cases become Molecule scenarios in the branch implementing that spec.
- Platforms: one macOS scenario and one Linux (Debian) scenario for this topic; the harness is the queued topic VM test-harness workstream (molecule/Vagrant per-topic scenarios: plan, scaffolding with an existing app scenario first, then the migration confirmation).
- Edge cases this spec requires covered: fresh apply brings the gateway up; idempotent re-apply (no duplicate bootstraps); adoption of a hand-started gateway without a second instance; reboot/re-login persistence — the service is actually loaded after restart (the macOS installed-but-not-loaded gap); respawn on gateway death (new pid, doctor green); teardown removes the service, kills hand-launched gateways, preserves the memory database; enable-linger reported but not changed; import ordering (env file before service, service before agents).
- Good tests assert external behavior — doctor output, a listening port, a changed pid, files present or absent — never playbook internals.
- The repo suite stays green alongside; Molecule adds the platform layer the suite cannot reach.

## Out of Scope

- The opencode plugin V2 port (upstream report, tracked on the queue; the interim stands until the port or the routing decision lands).
- Gateway authentication and token rotation (loopback-only deployment; a separate draft already records that decision).
- Any binding beyond loopback; remote or LAN clients.
- System-wide (non-per-user) service installs.
- The interim-routing decision itself — options and a lean are recorded, the call is the author's.

## Further Notes

- Implementing branch: PR #88 (loreai-gateway-service), carrying the leased gateway-service task (with its renumber track on the queue). The branch was mid-revision when this spec was written — hand its session this spec; do not edit its working tree.
- Investigation record (verified on macOS 2026-10-27): the service plist existed on disk but was NOT loaded in the gui domain — a manual `launchctl bootstrap` restored it and doctor went green. Treat bootstrap/enable persistence as unproven until the reboot scenario passes on both platforms.
- Linux rollout context: the CLI is identical cross-platform (`lore doctor` → `lore start --bg` → `lore run opencode` per session as the interim); the Debian half of the service is render-verified only until the rollout task applies it and the operator decides enable-linger.
- Tasks and PRs to get out: merge PR #88 once its Molecule scenarios pass; file the upstream plugin issue (text already drafted in its task); decide the interim routing (lean: chezmoi partial config — zero build, no per-project attribution until the upstream port); run the Debian backlog-cutover rollout; PR #92 (gita work-tree registration) is open and unrelated, queued for merge the same week.
