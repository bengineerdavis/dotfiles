---
id: DOT-282
title: Add a rust topic that installs rustup
status: Done
created_date: 2026-11-03 03:17
labels:
- now
priority: high
updated_date: 2026-11-05 03:51
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Author ruling 2026-11-04, restating and sharpening the 2026-11-01 Q1 direction: **rustup owns the Rust toolchain; mise syncs to it for any project we run.** rustup is the one canonical owner. mise keeps its `rust` entry as the project-level version selector that delegates to rustup — it does not become a second toolchain owner.

Measurement that settles the mechanism (2026-11-04): mise's `rust` key resolves to the `core:rust` backend, and that backend **already drives rustup**. Evidence:

- `readlink ~/.local/share/mise/installs/rust/1.99.0` → `/home/bdavis/.cargo/bin`
- `mise exec rust -- printenv RUSTUP_HOME` → `/home/bdavis/.rustup`
- `mise exec rust -- printenv CARGO_HOME` → `/home/bdavis/.cargo`
- `mise registry` → `rust core:rust asdf:code-lever/asdf-rust`
- `mise exec rust -- cargo --version` → `cargo 1.99.0`, rc=0

So rustup and mise already share one toolchain — but not through `mise sync`. Note
that `mise sync` has only `python`, `node`, and `rust` is absent:

```
mise sync --help
  node    Symlink node versions installed by nvm, nodenv, or Homebrew into mise
  python  Symlink python versions installed by pyenv or uv into mise
  ruby    Symlink ruby versions installed by Homebrew into mise
```

For rust the linking is built into the `core:rust` backend itself — that is why
`installs/rust/<version>` is a symlink into `~/.cargo/bin` rather than a private
toolchain copy. Any task or README written for this topic must say that, so nobody
adds a `mise sync rust` call that does not exist, and nobody "fixes" the symlink
into a real install and thereby creates the second channel this ruling forbids.

Precedent for the ownership model: DOT-113 (Shift Python ownership from mise to uv,
mise syncing) and DOT-112 (mise declares `topic_requires: [uv]`, plus an idempotent
`mise reshim`). This task is the same shape for rust, with the difference above:
rust needs no `mise sync` subcommand because its backend already symlinks.

The real gap is ownership: **no topic installs rustup.** On this machine it arrived
by hand in March 2025 and survives because `home/dot_zshrc.tmpl:335-336` sources the
untracked rustup-generated `~/.cargo/env`. A fresh or half-applied box has no
documented install story — `dotfiles/bootstrap/bootstrap.sh` installs no rust, and
`~/.cargo/env` does not exist until something creates it. `cargo` is not on a bare
PATH either (verified with `env -i`).

Scope of the topic:

- Install rustup through the official `rustup-init` path, per-user, Debian and macOS both targets, standard topic structure (`topic.yml`, `playbook.yaml`, `defaults/main.yaml`, `tasks/{main,bootstrap,prerequisites,install,remove,upgrade}.yaml`, `README.md`, `tests/topic-metadata.yaml`).
- Tier: `runtime-manager` — rustup manages a subordinate set of versioned toolchains, the same shape as mise managing versioned tools.
- `topic_provides: [rustup, rust, cargo]`, so any topic needing a compiler declares `topic_requires` instead of assuming one.
- `apps/mise` gains `topic_requires: [rustup]` and stops implying it supplies rust; its `rust = "latest"` entry stays, documented as the sync layer over rustup.
- Teardown removes only state the topic creates; adopt a pre-existing hand-installed rustup rather than reinstalling over it (probe-first, the `apps/uv` precedent).
- README states the ownership split so nobody later "fixes" mise into a second toolchain channel.

DOT-281 (lychee cargo fallback) depends on this: its cargo backend needs cargo to exist, and this topic is what guarantees that on a fresh box.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A fresh box installs rustup through the topic and `cargo` resolves on a bare PATH
- [ ] #2 `mise exec rust -- cargo --version` still resolves through rustup after the topic runs, with `RUSTUP_HOME` unchanged
- [ ] #3 macOS and Debian are both handled or explicitly gated
- [ ] #4 `apps/mise` declares `topic_requires: [rustup]` and the ownership split is stated in both READMEs
- [ ] #5 The topic adopts an existing hand-installed rustup instead of reinstalling over it, and a second run reports no change
- [ ] #6 Teardown removes only state the topic created and leaves a pre-existing toolchain intact
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Landed as PR #118. Investigation showed mise already installs rustup: its `rust`
key resolves to the `core:rust` backend, which downloads and runs rustup-init.
Proven on a clean HOME with empty .cargo/.rustup/MISE_DATA_DIR —
`mise exec rust -- cargo --version` fetched rustup-init, set the default
toolchain, and returned cargo 1.99.1.

So no rust topic was created. A topic running rustup-init would have been a
second installer for a channel mise already owns, which is the duplicate-channel
hazard AGENTS.md records for roborev.

What was actually missing was the declaration. `apps/mise/topic_provides` gained
rust, rustup, and cargo, so a topic declaring `topic_requires: [cargo]` resolves
instead of failing with TOPIC_NOT_RUN. Four tests in
tests/topics/test_rust_ownership.py hold it, each mutation-proven.

Not done: macOS was not run. The same backend would be used and rustup-init
publishes an aarch64-apple-darwin build, but nothing executed on the Mac.
That machine's real gap is Xcode Command Line Tools, which no topic installs.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
