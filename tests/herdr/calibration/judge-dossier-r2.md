You are the FINAL sign-off judge (fusion panel) for a test program. A prior
mid-round judge verdict was ITERATE with six gaps; all six have been triaged.
Your job: decide SHIP or ITERATE on the program as it now stands, and name any
NEW high-severity gaps the fixes introduced or missed. Return:

`VERDICT: SHIP | ITERATE`
then (only if ITERATE) numbered new gaps, each
`gap: <what> — severity: high|medium|low — fix: <one line>`
plus a one-line note on each of the six prior gaps: RESOLVED | ACCEPTED (with
why) | NOT-RESOLVED.

=== THE PROGRAM ===

A chezmoi+Ansible dotfiles repo. A new topic `herdr` was built TEST-FIRST: four
independent fresh-context agents deduced the contract from written artifacts
only and authored a failing-first suite; the topic was implemented to green.
Static suite (pytest over YAML/templates + an executable pure-Python contract
module the YAML is pinned against); 108 tests passing; the repo's real
converge passes are run by the human author (agents never apply) and are
queued.

Verification evidence:
- Red-first: every test failed with a named missing-artifact message before
  the topic existed; zero quiet skips.
- Six mutations each injected and caught (gate default, cursor probe,
  self-updater substitution, version-pinned shim path, dropped intersection,
  status parse swallowed); one nuance recorded: the gate-default mutation was
  caught by 2 of 3 candidate tests — the third's mutation note was corrected
  to name its true subject (contract-module gate semantics, not the defaults
  var, which the other two tests read).
- Wire format MEASURED on the real binary (herdr 0.9.1): status prints
  `<id>: installed|not installed (<path>)` lines, serverless, no --json; an
  earlier JSON assumption in the tests was corrected against the binary.

Round-1 gaps and their resolutions:
1. (high) No automated execution of the Ansible topic (converge/idempotence/
   remove human-only). → ACCEPTED, with a named home: the repo already queues
   molecule adoption for ALL topics (blocked on a --check fix); herdr is a
   candidate consumer, not the owner. Recorded in the topic README's
   verification section, not silently dropped.
2. (high) Contract module unvalidated against the real binary. → RESOLVED:
   golden-transcript test added against a REAL captured status output
   (18 agents, home-redacted fixture). The golden test immediately caught a
   wire variant the docs never showed — `letta (experimental): not installed
   (...)` — the parser accepts exactly that annotation and refuses any other.
3. (medium) Static scans do not expand Ansible loops/Jinja. → PARTIALLY
   RESOLVED + ACCEPTED: a real `ansible-playbook --syntax-check` test was
   added (run from the deployed-layout root, as the repo's run-role.sh does);
   full task-graph expansion stays with the molecule adoption. While wiring
   the YAML-side regexes for the measured grammar, a latent double-escaping
   bug was found in the ORIGINAL remove.yaml patterns (never would have
   matched) — fixed; it is concrete evidence for the judge's point about
   unexecuted YAML.
4. (medium) changed_when predicates untested (`mise upgrade` keys on `->`;
   `launchctl enable` marked changed_when false). → ACCEPTED: settled by the
   author's second-run idempotence pass, recorded in the topic CHANGELOG.
5. (medium) CRUD invariant was one-way. → RESOLVED: reverse-direction test
   added (orphaned teardown state fails).
6. (low) Gate-default mutation evidence. → RESOLVED: the third test's
   mutation note now names its true subject.

Also recorded during the build: a live cross-session collision on the shared
symlinked mise config (the just-added herdr entry was removed by another
process within a second and restored); the repo's hazard file documents this
file explicitly.

Known NOT exercised (stated in the topic CHANGELOG): real converge,
idempotence and remove on either machine; the server's own runtime behavior.
