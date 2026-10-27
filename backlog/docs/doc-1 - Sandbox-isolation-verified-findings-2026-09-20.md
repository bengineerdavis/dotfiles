---
type: research
tags:
- sandbox
- verified
id: DOC-1
title: Sandbox isolation — verified findings, 2026-09-20
---

## Sandbox isolation — verified findings, 2026-09-20

Measured on this machine, for the coordination work in § Now. Recorded because
the next session would otherwise re-probe it, and the `external_directory` deny
makes that expensive.

**Host attribution needs confirmation (2026-09-24).** The Linux-specific
measurements below do not establish capabilities on the current macOS host.
The September 24 comparison measured macOS only; Debian verification remains
open. Its report is committed at `.claude/RESEARCH-modular-agent-runtime.md`
on `main`.

- **This box supports unprivileged bubblewrap.** `bwrap`, `podman`, `docker`,
  `systemd-run`, `unshare` and `qemu-system-x86_64` are all on `PATH`;
  `firejail`, `lima` and `colima` are absent. `user.max_user_namespaces` is
  115796, and both `kernel.unprivileged_userns_clone` and
  `kernel.apparmor_restrict_unprivileged_userns` are absent — no
  Ubuntu-style userns restriction applies. The `overlay` module is present, so
  an overlayfs upperdir can serve as a write audit trail.
- **macOS has no equivalent, and that shapes the design.** No mount
  namespaces, no Landlock, no overlayfs. Seatbelt (`sandbox-exec`) is the only
  native path-level mechanism and is deprecated with an undocumented profile
  language, though Chromium, Bazel, Nix, Codex CLI and Claude Code all ship it.
  App Sandbox needs a signed bundle and cannot express an admin-supplied path
  list; Endpoint Security needs an Apple-granted entitlement and a system
  extension. So: **state the guarantee at the weakest platform**, make the
  portable git-level path gate the invariant, and treat bwrap/Seatbelt as
  defence in depth that turns a commit-time rejection into a write-time
  `EACCES`. A future `sandbox-exec` removal is then an inconvenience, not a hole.
- **Choose VM-backed execution by workload and configuration cost.** The
  earlier recommendation against a Linux VM default was too broad for the
  current brief. On 2026-09-24 the author accepted low-configuration non-root
  containers, including Sandcastle's approach, as primary candidates. Check
  host prerequisites, filesystem/watch behavior and native macOS dependencies
  for the actual workload. VM-backed containers are not limited to an optional
  high-assurance mode.
- **Subtree confinement exists; shared-writer safety is a different question.**
  The earlier ecosystem-wide absence claim was too broad. On macOS 26.6.2,
  SRT 0.0.77 allowed a synthetic write under `./allowed` while denying one at
  the workspace root. The research agent and coordinator reproduced this on
  2026-09-24. It does not isolate a shared index or a concurrently changing
  test tree, so it does not establish safe multi-writer use of one checkout.
- **Adopt, don't build** (AGENTS.md ladder): `anthropics/sandbox-runtime`
  wraps a process in Seatbelt-or-bubblewrap from one policy. Candidate source
  checks on 2026-09-24 changed the earlier descriptions: Treebeard couples
  worktree/overlay lifecycle and has no verified Debian backend; nixcage is
  Nix/VM infrastructure; sandnix uses Seatbelt/Landlock; cco selects backends
  but deliberately permits networking. The report carries pins and limits.
  Installed mise also has optional Seatbelt/Landlock controls, separate from
  its ordinary environment setup. Building another runtime here remains out
  of scope.
  Name collision to avoid: three different projects are called
  `sandbox-runtime` (Anthropic's, `carderne/`, and a Rust crate).
- **Destructive git operations defeat any path allow-list.** `checkout`,
  `restore`, `reset --hard`, `clean` and a stray `gc` destroy other agents'
  work while touching only permitted paths. This is the strongest argument for
  worktree-per-agent and for `.git` read-only inside worktrees.
- **Allow-list directories, not files** — editors, formatters and compilers
  write temp-file-plus-rename, which needs write permission on the directory.
- **The cheapest high-value control is not confinement.** An out-of-scope write
  is recoverable from git; `push --force`, `gh pr merge` and `npm publish` are
  not. Deny push to protected refs and require human merge.
- **The chezmoi deployed tree is the gap the portable layer cannot see.**
  `~/bin` and `~/dotfiles` live outside the repo, so a git-level gate cannot
  detect a `chezmoi apply` violation — only OS confinement can. That is the
  strongest reason to keep bwrap despite its cost.
