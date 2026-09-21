You are calibrating as a test-review judge. Below is a topic's contract, then
six test excerpts (A–F). For EACH item return one line:

`<letter>: SOUND | DEFECT — <one-sentence reason> — severity: high|medium|low`

Do not summarize the contract. Judge only what each excerpt asserts versus
what the contract requires.

=== CONTRACT (the topic must do exactly this) ===

The herdr topic installs the herdr binary through mise (entry in the global
mise config, idempotent: probe first, then `mise use -g herdr`; remove runs
`mise unuse --global herdr`). It never calls `herdr update`. A shared
catalogue `agents.yaml` lists agent integrations (id, probe binary, config
dir). On install, the topic loops the catalogue entries: for each entry where
the probe binary is on PATH AND the agent's config dir exists, it runs
`herdr integration install <id>`; when either probe fails it reports SKIPPED
and continues (never fails the run); if the herdr binary itself is missing
after install, the run RAISES with the fix named. On remove, it uninstalls
integrations only where catalogue-claimed AND actually installed
(intersection), gated behind `herdr_remove_integrations: false` default. The
service: launchd per-user agent on macOS / systemd user unit on Debian,
pointed at the stable mise shim path, RunAtLoad+KeepAlive, health-checked
after boot; teardown order is service first, then integrations, then the mise
entry. The slice resolution from the catalogue is a pure function: union of
unscoped entries plus entries scoped to herdr, minus the ignored list. Guards
must be proven to relent BOTH directions: decline when they must, proceed
when they may.

=== TEST EXCERPTS ===

A) test_integration_loop_proceeds_when_agent_present:
```yaml
- name: install opencode integration when probe and config dir exist
  command: herdr integration install opencode
  when: herdr_opencode_probe.rc == 0 and herdr_opencode_dir.stat.exists
```
A companion test asserts: when the probe returns rc=1, the loop task is
skipped, SKIPPED is reported, and the run exits 0.

B) test_install_skip_is_reported_and_run_stays_green:
```yaml
- name: "all integrations skipped when agents absent"
  assert:
    that:
      - herdr_install_failures | length == 0
```
(no companion test asserts an entry IS installed when its agent is present)

C) test_remove_uninstalls_claimed_integrations:
```yaml
- name: remove catalogue-claimed integrations
  command: herdr integration uninstall {{ item }}
  loop: "{{ herdr_remove_ids }}"
```
(installed-list intersection omitted)

D) test_service_removed_before_binary:
```yaml
- name: remove launches service teardown, then entry removal
  assert:
    that:
      - remove_tasks.index('stop service') < remove_tasks.index('mise unuse')
```
companion asserts reverse order still fails the test when mutated.

E) test_slice_resolution_property:
```python
@given(st.lists(catalogue_entries()), st.just(IGNORED))
def test_slice_is_union_minus_ignored(entries, ignored):
    assume(len(entries) > 0)
    result = resolve_slice(entries, scoped="herdr", ignored=ignored)
    assert set(result) == (
        {e.id for e in entries if not e.scoped}
        | {e.id for e in entries if e.scoped == ["herdr"]}
    ) - set(ignored)
```
(resolve_slice reimplemented inline in the test, line-for-line)

F) test_status_parse_failure_reports_unknown:
```python
def test_parse_status_returns_empty_on_unparseable_output():
    assert parse_integration_status("gibberish") == {}
```
and the remove loop treats an empty parse as "nothing installed",
uninstalling nothing, exiting 0.
