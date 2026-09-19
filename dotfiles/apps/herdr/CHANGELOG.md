# CHANGELOG

## Unreleased

- 2026-09-19: **Support grade for `community.general.launchd`: A** — the
  four checks from the module-vs-shell ladder
  (`dotfiles/docs/TOPIC-RECIPES.md`): maintainer named + two launchd
  changelog entries in the current release (PRs #11049, #11774);
  integration target present; no removal/redirect in `meta/runtime.yml`;
  check_mode full and source-read verified. No new galaxy dependency — the
  collection was already declared. Shell/cmd fallbacks ratified the same
  day (CLI invocations, grep -q, command -v, systemctl is-active);
  `systemctl --user cat` swapped to `ansible.builtin.stat` as the one
  module upgrade the ladder found.

- 2026-09-19: **Converge pass 1 (author-run, partial): launchd management
  switched to the native module.** The pass verified: the `mise upgrade`
  changed_when predicate (all up to date → changed=false), entry-probe
  idempotence, slice resolution, the cursor skip-and-report verdict line
  (naming both conditions), and real integration installs (opencode plugin +
  tui.jsonc; claude hook + settings.json). It then failed at the launchd
  step: `ansible_facts['user_id']` resolves to the USERNAME, so
  `launchctl print gui/<user_id>/...` was an unrecognized target. The raw
  probe/bootout/bootstrap/enable chain is replaced by
  `community.general.launchd` (restarted + enabled on install; stopped +
  force_stop + enabled=false on remove behind a plist stat guard) — the
  module needs no domain targeting, restarts on plist change, and flips
  KeepAlive before stop. Stated tradeoff: the module uses the legacy
  load/unload verbs (deprecated upstream); ollama's raw modern verbs are
  unaffected. Also fixed: the classification reason no longer says
  "skipped" on installable rows. Honest gap: `--syntax-check` validates
  task structure, not module-arg names — the remove pass would have caught
  a stray invalid arg (none remains); module-arg validation is runtime
  territory, which is the molecule case.

- 2026-09-19: **Completion path corrected post-report**: `~/.zfunc` is on
  nobody's fpath in this repo (`dot_zshrc.tmpl:96` puts
  `~/.local/share/zsh/completions` on fpath), so the generated completion
  would have been written and never loaded. The topic now generates to
  `~/.local/share/zsh/completions/_herdr` (`herdr_completion_path` in
  defaults), and the tests pin the var chain + the fpath fact. Found by
  checking the zsh runtime after the report; README decision updated with
  the same evidence.

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
