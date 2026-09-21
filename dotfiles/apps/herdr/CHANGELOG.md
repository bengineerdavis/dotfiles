# CHANGELOG

## Unreleased

- 2026-09-19: **Machine passes complete — the topic is proven on this Mac.**
  Converge after the upgrade-relent fix: `ok=25 changed=5 failed=0` (entry
  re-added, plist/launchd/completion/log-dir recreated, health check green,
  integrations pre-read as current). Remove: `ok=8 changed=4 failed=0` —
  the gate-off teardown proven live (integrations stay, service stops,
  plist/completion removed, mise entry pruned). The upgrade-relent fix was
  exercised for real: the post-remove re-converge hit the dangling shim and
  skipped-with-report instead of dying (that first attempt's failure
  produced the fix). Recorded corrections: 1336766 accidentally committed
  the entry removal (staging verified the diff existed, not its content) —
  corrected in abfb799; the earlier `ok=1` converge recap attributed to
  running the runner from the wrong cwd (no such topic playbook). Golden
  fixture matches the live state (opencode v12, claude v10) — no
  reconciliation needed.

- 2026-09-19: **Converge pass 1 (complete): server running; pre-read regex
  double-escape caught by the recap and fixed.** Recap: ok=24 changed=2
  failed=0. The launchd module task worked end to end (unloaded → started,
  pid 55783; health check `status: running, v0.9.1`); the version-floor
  check ran (empty `--outdated-only` → no raise). The `changed=2` was the
  two integration installs reporting changed because the install pre-read's
  Jinja regex carried the double-escape class AGAIN (`\\(v\\d+\\)` in the
  folded scalar — the engine sees literal backslashes and never matches), so
  `herdr_preinstalled_ids` resolved empty against a status read that
  visibly showed `current (v10)`/`current (v12)`. Fixed in both task files,
  execution-verified against the real output, and a new test now compiles
  the task YAML's own regex strings against the golden fixture — the class
  has bitten twice and static scans cannot see it; this test executes the
  strings (mutation-checked in its comment). No static test can validate a
  regex string's escaping; only compiling it does.

- 2026-09-19: **Wire grammar grew with the fixture refresh; loop idempotence
  fixed before pass 2.** Re-capturing the golden fixture after the first
  converge showed the real installed-state form: `current (v12) (...)`, not
  `installed (...)` — the remove-side regex would never have matched a real
  installed integration. Grammar everywhere now accepts
  `not installed` / `current (vN)` (+ the letta `(experimental)` annotation);
  `outdated (vN)` stays OUT of the grammar (unmeasured → unknown → refuses,
  fail-closed). The install loop now reads integration state BEFORE the loop
  and keys changed_when per entry on that pre-read — measured: herdr's
  re-install prints the same lines as a first install, so a bare
  `changed_when: true` would report the loop changed on every converge and
  break the changed=0 pass (mutation M8 proven). The upgrade pass now
  enforces the catalogue's native-restore floors via
  `herdr integration status --outdated-only`, raising with the named fix
  (extension-after-adoption rule; the CLI's own currency check, no module
  exists). Golden fixture now records the real post-converge map: opencode
  and claude installed (v12, v10 — above their floors 5 and 6), the rest not.

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
