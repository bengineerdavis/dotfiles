# apps/loreai — gateway-service Molecule scenario (Debian)

Run through the repository wrapper:

```bash
MOLECULE_SCENARIO=debian scripts/run-molecule.sh loreai test
MOLECULE_SCENARIO=debian scripts/run-molecule.sh loreai create
MOLECULE_SCENARIO=debian scripts/run-molecule.sh loreai login
MOLECULE_SCENARIO=debian scripts/run-molecule.sh loreai destroy
```

The scenario uses `debian/bookworm64` under Vagrant/libvirt. `converge.yml`
runs the real role with `loreai_telemetry=0` and `loreai_inference=none`, so
no LLM credential or agent CLI is needed. Molecule's idempotence action runs
the install a second time.

`side_effect.yml` then exercises the service's external behavior: active and
enabled after a fresh apply; replacement of the hosted hand-started gateway
with a local service-owned instance while the service stays active; a
simulated binary upgrade that
stops the adopted process; respawn with a new pid after `lore stop`; a loud
health-check failure on non-default port 5673 followed by
recovery to 3207; doctor green after a real VM reboot; linger
unchanged; and teardown while a hand-launched gateway is running. It calls
remove a second time to prove that a missing unit and binary are tolerated.

The testinfra verifier runs last and asserts the teardown contract: unit,
binary, listener, and topic-owned state gone; the memory database preserved.

The approved VM harness has no macOS Vagrant-box mechanism
(`dotfiles/docs/research/topic-vm-tests/PLAN.md`), so this is the Debian leg
only. The Darwin behavior is covered by the service-command pytest seam and
the live macOS apply, not by a macOS VM run.
