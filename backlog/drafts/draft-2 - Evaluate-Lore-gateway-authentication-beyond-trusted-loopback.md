---
id: draft-2
title: Evaluate Lore gateway authentication beyond trusted loopback
status: Draft
created_date: 2026-10-28 01:24
labels:
- loreai
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Lore documents LORE_GATEWAY_AUTH_TOKEN as an optional bearer token for remote/hosted data-plane requests, sent as x-lore-gateway-token. Local loopback mode deliberately disables gateway access authentication; there is no username/password or timed-token mechanism. A persistent loopback listener does not warrant token rotation because any local process able to read a refreshed token can already read the existing per-machine env file.

Ship:

- Record the supported token mechanism and the decision not to add rotation for loopback.
- Revisit only if the gateway binds beyond loopback, team-sync or LAN clients are introduced, or untrusted local processes enter the threat model.

Constraints:

- Keep this as a long-term draft while the gateway remains loopback-only.
- Do not enable a token without verifying every client's header support and restart requirements.

Agreed with the maintainer 2026-10-27: do not overthink loopback authentication; track only the documented remote-mode option and its triggers.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The draft names LORE_GATEWAY_AUTH_TOKEN, the lack of timed tokens, and all three revisit triggers.
- [ ] #2 No token rotation or client reconfiguration is implemented for the current loopback-only deployment.
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
