---
id: DOT-332
title: apt_keyring.py must update signed-by= when it corrects a .asc to .gpg
status: To Do
created_date: 2026-11-09 00:00
labels:
- apt
- keyring
- bug
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`apps/apt/files/apt_keyring.py` now corrects a `.asc`-named destination to its
`.gpg` sibling when the dearmoured key is binary (PR #157), but it writes the
key to `.gpg` and leaves the source's `signed-by=` pointing at `.asc` — which
still holds the old content. The report says "repaired" while apt still fails.

The helper reports the correction in `detail`, but that is a human nudge, not a
repair. Two candidate resolutions:

1. **Update the source** — when the helper corrects a `.asc` → `.gpg`, also
   rewrite the matching `signed-by=` (or `Signed-By:`) line in the source file
   to point at the `.gpg` path, so the correction is complete and apt works
   immediately.
2. **Refuse loudly** — treat a `.asc`-named binary destination as unrepairable
   (exit 2, clear stderr), forcing the author to fix the source, rather than
   half-writing.

Option 1 is the true "repair it" behaviour and matches the helper's charter
(a download that is not a key never reaches the destination). Option 2 is the
fail-closed alternative if editing sources in-place is judged too invasive.

Done when a repo whose source names `signed-by=/etc/apt/keyrings/docker.asc`
but serves a binary key is left in a working apt state — either the source is
repointed to `.gpg`, or the helper refuses with a message naming the exact
line to fix. The `test_asc_dest_is_corrected_to_gpg` test is extended to
assert the source reference was updated (or that refusal was raised), not just
that `docker.gpg` exists.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- SECTION:ACCEPTANCE:BEGIN -->
- [ ] After a `.asc`→`.gpg` correction, the source's `signed-by=` points at the `.gpg` file (or the helper refuses naming the fix)
- [ ] The report status does not read "repaired" unless apt is left working
- [ ] test_asc_dest_is_corrected_to_gpg asserts the source reference, not only the file
<!-- SECTION:ACCEPTANCE:END -->

## Related

- PR #157 — the `.asc`→`.gpg` correction and the docker `.gpg` write (this task is the deferred half)