# CHANGELOG

## Unreleased

- 2026-09-19: **Mutation log** (spec.md § Verification — every mutation
  injected, watched going red, and restored; suite back to 105 passed after
  each):
  - M1 gate default flipped to `true` → caught by
    `test_remove_integrations_gate_defaults_off` +
    `test_remove_gate_defaults_off`; the catalogue-level
    `test_remove_defaults_to_no_uninstall` survived because it exercises the
    contract module's gate semantics, not the defaults var — the default is
    covered by the other two.
  - M2 cursor probe weakened to `cursor` → caught by
    `test_wired_entry_facts_match_upstream_docs`.
  - M3 `herdr update` substituted for `mise upgrade` → caught by
    `test_never_herdr_update_and_upgrade_routes_through_mise` +
    `test_upgrade_routes_through_mise_and_never_self_updates`.
  - M4 version-pinned `mise/installs/` path in the launchd plist → caught by
    `test_launchd_plist_shim_runatload_keepalive`.
  - M5 remove intersection replaced by the whole installed set → caught by
    `test_remove_uninstall_set_is_the_claimed_intersection` (the test added
    when this gap was found).
  - M6 status parse swallowing garbage as `{}` → caught by 8
    `test_status_garbage_is_unknown_never_a_claim` cases.
- 2026-09-19: **Wire format measured on the real binary** (herdr 0.9.1,
  2026-09-19): `herdr integration status` prints lines of
  `<id>: installed|not installed (<path>)`, works without a running server,
  and `--json` is a usage error. The suite's original JSON-shape assumption
  was corrected against the binary (evidence over assertion).
- 2026-09-19: Topic created against the swarm-authored suite in
  `tests/herdr/` (test-first: the suite was red against this directory before
  any topic file existed, and the topic was implemented to green). Design
  record: `README.md` in this directory; generalized decisions:
  `dotfiles/docs/TOPIC-RECIPES.md`.
- 2026-09-19: Teardown order pinned as **integrations → service → entry**
  (README § Structure; `tests/herdr` pins it in two dimensions). The
  load-bearing invariant is service-stop-before-unit-file-removal; the entry
  removal is last because it prunes the binary nothing above it needs.
- 2026-09-19: Known-open predicates the author's converge pass settles:
  `mise upgrade` changed_when keys on `->` in output (verify against real
  mise output); `launchctl enable` is marked changed_when false (idempotent
  no-output command).
