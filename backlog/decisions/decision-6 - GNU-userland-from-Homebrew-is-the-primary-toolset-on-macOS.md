---
id: decision-6
title: GNU userland from Homebrew is the primary toolset on macOS
date: 2026-11-17 16:50
status: accepted
---

## Context

The fleet is macOS and Debian/Ubuntu and will grow as hardware is added or
replaced. Scripts that behave differently per OS are the most common
cross-platform bug here: BSD and GNU differ for `sed -i`, `stat`, `mktemp`,
`script` and others (`docs/CROSS-PLATFORM.md`), and macOS ships bash 3.2
(DOT-327).

The `gnu-tools` topic prepends the Homebrew GNU `gnubin` directories
(coreutils, gnu-sed, gnu-tar, grep, findutils) to `PATH` through its
`path.zsh`. But that file only runs in an interactive zsh. Measured
2026-11-17 on the managed Mac: `zsh -ic 'command -v sed'` gives the GNU
`gnubin/sed`, while `zsh -lc`, `/bin/sh`, launchd jobs and Ansible tasks give
`/usr/bin/sed` (BSD). The topic's `install.yaml` and `remove.yaml` are
commented-out skeletons (`docs/CRUD-AUDIT.md`), so the packages arrive only
through `brew-bootstrap` or by hand.

## Decision

Author ruling 2026-11-17: on macOS, the Homebrew GNU tools (and Homebrew bash,
DOT-327) are the primary userland. This is deliberate fleet strategy: the same
tools and the same bash on every machine, Mac or Linux.

## Consequences

- The `gnu-tools` topic must own its packages: a real install and remove, not
  skeletons.
- Interactive shells already get GNU first. Non-interactive contexts (login
  shells, `/bin/sh`, launchd, Ansible) still get BSD until GNU reaches their
  `PATH`, so scripts must not assume either dialect there until that lands.
- Agents check the dialect with `<tool> --version` rather than assuming one,
  and write GNU forms in interactive and repo tooling.
- Linux needs no change: GNU is already native.
