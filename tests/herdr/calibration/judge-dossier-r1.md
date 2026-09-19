You are the mid-round judge for a test program. Your job: find HIGH-severity
gaps in the TEST PROGRAM (coverage holes, tests that could pass vacuously,
contract/implementation divergence risks). Not a style review. Return:

`VERDICT: SHIP | ITERATE`
then numbered gaps, each `gap: <what> — severity: high|medium|low — fix: <one line>`.
If you find no high-severity gaps, say so explicitly.

=== THE WORK ===

A chezmoi+Ansible repo (dotfiles machine management). A new topic `herdr` was
built TEST-FIRST: four independent fresh-context agents deduced the contract
from written artifacts only (design README, recipes doc, repo spec, upstream
docs) and authored a failing-first suite; the topic was then implemented to
green. The suite runs statically (pytest over YAML/templates; an executable
pure-Python contract module the YAML is pinned against; no ansible execution
in tests — real convergence passes are run by the human author, queued).

Suite (105 tests, all passing):
- test_lifecycle_contract.py (17): topic.yml five-field schema; tag router
  (remove tagged [remove, never]; both directions proven); CRUD/teardown
  invariant derived by PARSING install.yaml (created file paths and command
  markers each must have a remove.yaml counterpart); teardown order
  (integrations < service < entry by task index); stop-before-unit-removal;
  gate default off; every uninstall task relents through the gate;
  upgrade routes via `mise upgrade`, never the tool's self-updater;
  integrations only after the entry; the topic never file-writes another
  topic's tracked config (mise entry only via first-party mise commands);
  the remove-side intersection pinned to the YAML.
- test_catalogue_integrations.py (18): agents.yaml schema (editors.yaml
  pattern: version/agent_integrations/agent_integrations_ignored; entry =
  id/why/probe/config_dir/kind/topics/min_version{version,checked});
  wired set exactly {opencode, claude, cursor}, per-entry facts vs upstream
  docs (cursor probes `cursor-agent`, kinds lifecycle/session, native-restore
  floors 5/6/1 recorded dated); all 18 upstream ids wired-or-ignored; slice
  resolution as first-principles properties (idempotence, subset,
  ignored-disjoint, two independent constructions must agree); skip-vs-raise
  loop simulated (gate proceeds when probe+dir present, declines+reports each
  id with exit 0, AND-semantics matrix, raises naming `mise use -g herdr`
  when herdr missing); gated intersection removal (gate-off → nothing;
  unclaimed machine-held ids left alone; claimed-but-absent → no call).
- test_user_acceptance.py (17): every README-named structure file exists;
  StrictUndefined jinja2 renders of both service templates under BOTH
  os_family values (vars fed from the topic's defaults, ansible facts
  stubbed); launchd plist pinned to the STABLE mise shim path (never
  version-pinned), RunAtLoad+KeepAlive, `herdr server` subcommand; systemd
  USER unit (no multi-user.target, no User=); never-herdr-update scan over
  code lines (comments stripped) + positive `mise upgrade` routing; exact
  `mise use -g herdr` present with probe-registered BEFORE it and a `when:`
  guard; `mise unuse --global herdr` in remove; config template has exactly
  update.channel="stable" + [session] resume_agents_on_restore=true, no
  secrets (regex incl. auth_token class), no employer literals anywhere in
  the topic tree; completion to ~/.zfunc/_herdr (never the zsh tree), remove
  takes it out; README cross-links.
- test_edge_stress.py (18 functions / 52 cases): catalogue fuzzing (unknown
  verdict statuses, missing fields, duplicate ids, 15 hostile entry shapes —
  validator must reject naming file+field, never coerce); hostile status
  output (empty/whitespace/prose/truncated/control-char/missing-path/dup-id/
  unknown-state-word → UNKNOWN, never a claim; valid lines parse exactly);
  remove_plan rc doctrine (nonzero refuses naming rc; 2 = usage error; rc0
  garbage refuses); skip names BOTH conditions; failures collected and
  raised once naming all; rc=2 usage errors never retried; teardown over
  hostile partial state converges and second run is a no-op; nothing-ever-
  installed remove is a clean no-op both gate states; scale property (1..200
  entries, one planned command per entry, unique, catalogue order);
  generated-duplicate rejection property; static scan: no rc-masking pipes
  in task YAML.
- agents_contract.py: executable contract module (validation, planned
  commands, status parse, install loop, remove plan, teardown plan) the YAML
  is pinned against from two other dimensions.

Evidence of non-vacuity: the suite was RED before the topic existed (every
test failing with a named missing-artifact message); 6 documented mutations
were each injected and caught (gate default, cursor probe, herdr-update
substitution, version-pinned shim path, intersection dropped, status parse
swallowed) — one nuance: the gate-default mutation was caught by 2 of 3
candidate tests; the third exercises the contract module's gate, not the
defaults var, and its subject was not the mutated line.
Wire format was MEASURED on the real binary (herdr 0.9.1): `herdr
integration status` prints `<id>: installed|not installed (<path>)` lines,
no server needed, no --json flag — an earlier JSON assumption in the tests
was corrected against the binary.

Known NOT exercised (stated honestly in the topic CHANGELOG): real converge
on either machine (converge, second-run idempotence, remove — the human
author runs those; agents never apply); the `mise upgrade` changed_when
predicate (keys on `->` in output) and `launchctl enable` changed_when
false; the herdr server's own runtime behavior.

An unrelated hazard event occurred during the build: the shared
symlinked mise config was rewritten by another process mid-edit (the
just-added herdr entry was removed within the same second and restored) —
the exact cross-session hazard the repo records for that file.
