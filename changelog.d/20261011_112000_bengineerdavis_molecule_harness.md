**Added**

- A molecule + Vagrant topic-test harness: `scripts/run-molecule.sh <topic>
  [verb]` drives per-topic molecule scenarios from anywhere, through the new
  locked `test-vm` uv dependency group (molecule 26.9.0,
  molecule-plugins[vagrant] 26.9.28, pytest-testinfra 10.2.2,
  ansible-core 2.21.5) with `community.vagrant` 1.0.1 pinned in
  `dotfiles/requirements.yml`. First scenario: `apps/opencode` — vagrant
  boots `debian/bookworm64` under libvirt/KVM, prepare bootstraps the box to
  the pre-migration state (apt, linuxbrew, mise+node, chezmoi, the v1
  formula), converge imports the topic role, and pytest-testinfra asserts the
  v2 migration's end state (v2 formula installed, v1 gone, `opencode
  --version` 2.x, the migrated config loads with its ordered permissions
  array, skills synced, tap trusted). Scenarios live inside the topic at
  `apps/<topic>/molecule/default/` per the recorded molecule-adoption
  conventions; a `test-vm` run provisions a VM one box at a time and never
  touches the host beyond the user-level ansible collections directory.