---
id: DOT-292
title: Review Lychee external-link validation security policy
status: To Do
created_date: 2026-10-29 06:08
labels:
- security
- docs
- lychee
references:
- https://lychee.cli.rs/guides/config/
- https://lychee.cli.rs/recipes/links/
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Author direction: documentation may use external web references and Lychee should validate those links, as an explicit exception to the normal offline-only link check. Review the proposed policy with a Roborev security review before implementation. Prefer safe but permissive behavior for public web references: validate local Markdown links and anchors, check public HTTP(S) references, deny requests to private, loopback, link-local, and local destinations, and do not enable archives, link replacement, credentials, cookies, custom authorization headers, or email checks. Treat URLs and their query strings as disclosed to their destinations. Assess DNS-rebinding and redirect-to-private-address risks, configuration enforcement, secrets in URLs, rate limits, CI/network behavior, and the tests needed to prove the restrictions. A security review is advisory, not a substitute for deterministic configuration tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document the allowed external HTTP(S) link-checking scope and the rationale for the exception.
- [ ] #2 Review private-network, redirect, DNS-rebinding, credential, URL-disclosure, and CI availability risks.
- [ ] #3 Specify deny rules for private, loopback, link-local, and local destinations, including redirects.
- [ ] #4 Define local and external check commands and tests that distinguish expected link failures from network or policy failures.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Roborev security findings have been reviewed with the author and resolved or explicitly accepted.
- [ ] #2 The selected Lychee configuration and verification plan are recorded before implementation.
<!-- DOD:END -->
