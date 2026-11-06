### Added

- Provisioning answers for the loreai topic now live in `machines.yml`'s
  `provisioning` registry (shared fleet defaults plus per-host exceptions),
  so a machine answers once and later runs are unattended. A machine whose
  hostname cannot be committed (a hardware serial) keeps its machine tier in
  an unversioned local overlay.

### Changed

- `env.zsh` is an artifact of the registry rather than a source of truth; a
  registry-driven re-run re-renders it byte-identically.
- Repo membership moved from `machines.yml`'s per-machine block to the single
  shared catalogue `config/repos.yaml`; the per-machine block had no consumer.
- Machine keys are hostnames only where the hostname passes the employer
  string test. The committed hardware-serial keys in `.chezmoidata/uv.yaml`
  and `.chezmoidata/opencode.yaml` are removed (both were no-ops on the Mac).
