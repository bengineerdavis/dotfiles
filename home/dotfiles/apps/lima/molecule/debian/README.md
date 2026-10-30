# Debian scenario: host, guest, and teardown

The scenario tests a real Linux VM. It does not run Molecule inside the VM,
and it does not give the guest responsibility for the host lifecycle.

## Who owns what

| Component | Runs on the controller host | Runs inside the Linux guest |
|---|---|---|
| Molecule | Drives the scenario phases and connects to the guest | No |
| Ansible | Executes host-local setup and teardown; connects to the guest for guest tasks | Executes guest-side configuration and assertions through Ansible |
| Lima | Creates, stops, and deletes the VM | No |
| Linux guest | Is created and managed by Lima on the host | Provides the isolated Debian environment under test |

The delegated VM model means that Molecule remains on the controller and
Lima manages the VM on its behalf. The guest does not create a nested VM,
manage its own outer lifecycle, or clean up the controller.

```text
Controller host
  Molecule drives the scenario
  Ansible runs host-local lifecycle tasks
  Lima creates and stops the Linux guest
        |
        | SSH
        v
Linux guest
  Runs Debian configuration and verification tasks
```

On the verified macOS run, the controller was macOS but the test guest was
Linux: Debian 12.15, aarch64, QEMU, with a running systemd user manager.
The guest assertions are in `verify.yml`; they are evidence about the test
environment, not evidence that the guest owns VM creation.

## Scenario phases

`molecule.yml` orders the phases as follows:

1. `create.yml` installs the Lima topic into an isolated controller home,
   creates the scenario's Lima home, starts the rootless VM, and gives
   Molecule the guest SSH connection.
2. `converge.yml` applies the topic again to check idempotence and plants a
   sentinel that later teardown must preserve.
3. `side_effect.yml` tests the topic's removal lifecycle and checks that
   user VM data and shared QEMU survive. It reinstalls the controller CLI
   needed by teardown. `verify.yml` asserts the guest's Debian, QEMU, and
   systemd-user properties.
4. `cleanup.yml` removes only the scenario's disposable home after VM
   teardown. The controller's Lima installation remains available to
   `destroy.yml`.
5. `destroy.yml` stops the scenario VM and removes its temporary state.

## Teardown must wait for processes

A stop or force-delete command can return before Lima's processes have
actually exited. Deleting the temporary Lima home at that point leaves live
processes referencing removed state and makes cleanup look successful while
leaking resources.

The scenario therefore performs these steps in order:

1. Read the scenario's host-agent and QEMU PIDs before stopping it.
2. Stop only the scenario's named VM and host agent.
3. Wait for the recorded PIDs to exit; if necessary, force-stop and wait
   again. Fail if a process remains alive.
4. Delete the scenario VM and temporary Lima home.

The wait distinguishes "stop requested" from "processes have exited." Only
scenario-owned VMs, processes, and temporary paths are targeted; unrelated
Lima and Rancher Desktop state must remain untouched.

## Tests and limits

`tests/lima/test_lima_lifecycle.py` exercises the scenario's static
contracts, including the teardown ordering. The full
`MOLECULE_SCENARIO=debian scripts/run-molecule.sh lima test` run proves the
real lifecycle on the controller and records its guest and cleanup evidence.
It does not by itself prove application on a Linux controller; that remains
separate verification work.

The Lima topic belongs only under `home/dotfiles/apps/lima`. Keeping a
second copy under the old `dotfiles/apps/lima` path would make the deployed
topic ambiguous after the payload migration.
