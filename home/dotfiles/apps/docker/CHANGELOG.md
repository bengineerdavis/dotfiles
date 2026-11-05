# docker — changelog

This topic's own history. See `docs/TOPICS.md` § "Per-topic changelog and local
edge cases". Section names follow antsibull-changelog.

## Unreleased

### bugfixes

- 2026-11-02: install no longer asks apt for Ubuntu's `docker.io` +
  `docker-compose-v2`. That stack is mutually exclusive with the docker-ce
  stack this topic manages: `docker.io` depends on Ubuntu's `containerd`,
  which conflicts with Docker's `containerd.io`, and `docker.io` itself
  conflicts with `docker-ce` — on a host already running the official
  packages apt died with "E: Error, pkgProblemResolver::Resolve generated
  breaks" (seen 2026-11-01). `docker-compose-v2` also ships the same plugin
  file as `docker-compose-plugin`, so those two can never coexist either.
  install.yaml now adds Docker's official repo and installs the CE stack
  (docker-ce, docker-ce-cli, containerd.io, docker-buildx-plugin,
  docker-compose-plugin, docker-ce-rootless-extras).

### minor_changes

- 2026-11-02: the topic owns its whole apt story — repo (deb822
  `/etc/apt/sources.list.d/docker.sources`), signing key
  (`/etc/apt/keyrings/docker.asc`), and packages — instead of assuming the
  repo was configured by hand. A pre-existing one-line
  `/etc/apt/sources.list.d/docker.list` is retired on install so the repo is
  not configured twice. remove.yaml mirrors all of it (packages → repo →
  keyring).
- 2026-11-02: the apt topic's `apt_keyrings` now also covers
  `download.docker.com`, so a rotated Docker signing key is repaired before
  the cache refresh instead of failing it (see apps/apt/CHANGELOG.md).
- 2026-11-02: new tunable `docker_apt_lock_timeout` (default 300s) for the
  same PackageKit lists-lock race apps/apt raised its own timeout for on
  2026-09-20.
- 2026-11-03: `docker_apt_distro` defaults to the Debian path; only the
  recognized Ubuntu family (`docker_ubuntu_family`) opts into the /ubuntu/
  repo. Docker publishes per-distro suites (the /debian/ repo has no jammy),
  so the path must follow the base distro — the docker-ce packages
  themselves are identical and portable either way. Repo-wide standing
  policy recorded the same day (see policy/personal.yaml § packaging): snap
  banned, portability across the Linux/Unix family required, Debian-proper
  mechanisms the default.

### known_issues

- Pop!_OS reports the Ubuntu codename as `ansible_distribution_release`
  (`jammy` on 22.04) and this topic relies on that: Docker publishes no pop
  repo, so the Ubuntu suite is used directly — matching Docker's own install
  docs for Pop!_OS. Linux Mint would report a Mint codename and is out of
  scope.
