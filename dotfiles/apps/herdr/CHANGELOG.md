# CHANGELOG

## Unreleased

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
  no-output command); the `herdr integration status` wire shape
  (`{integrations: [{id, installed}]}` or bare array) is a stated assumption
  to verify on the real binary.
