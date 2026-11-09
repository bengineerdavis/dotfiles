---
id: DOT-327
title: Own a bash topic on macOS so the machine uses Homebrew bash, not the 3.2 that ships with it
status: To Do
created_date: 2026-11-08 17:40
labels:
- cross-platform
- tooling
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
macOS ships `/bin/bash` at **3.2.57**, released 2007, and Homebrew's `bash` is
installed but **nothing owns it as a topic**. The result is that 36 scripts in
this repo get whichever bash is first on `PATH`, and on a fresh Mac that is the
2007 one.

This is not hypothetical. It bit PR #148: `"${TIMEOUT_CMD[@]}"` on an empty
array is an unbound-variable error under bash 3.2 with `set -u`, so the wrapper
would have died on the `login` path on any Mac. The fix worked around the shell
rather than fixing which shell runs — which is the right call for one script,
and the wrong resting place for 36.

**What exists today, verified not recalled.**

- `home/bin/executable_brew-bootstrap:535` runs `brew install bash`, so the
  binary is often present. Its only acknowledgement of the shell afterwards is
  a `detect_bash_version` report and an advisory line (`:708`) telling the
  reader to install modern bash.
- `home/dotfiles/apps/homebrew/tasks/prerequisites.yaml:23` installs the core
  Homebrew packages — `git curl wget ca-certificates gnupg coreutils` — and
  **bash is not among them**. So bash arrives only if the standalone bootstrap
  script was run, not from a normal Ansible pass.
- **No bash topic exists** (`home/dotfiles/apps/` has no `bash` entry), so
  nothing declares ownership, nothing installs it on a machine that skipped the
  bootstrap, and nothing teardowns it.
- Nothing adds `/opt/homebrew/bin/bash` to `/etc/shells`, and nothing makes the
  login shell the Homebrew build.

**Why PATH is the lever, not the login shell.** All 36 scripts check out with
`#!/usr/bin/env bash`, which resolves through `PATH`. So
`/opt/homebrew/bin` before `/bin` is what makes them run on a modern bash, with
no shebang edits and no `/etc/shells` change. Changing the *interactive* login
shell is a separate question with a separate blast radius (it affects `$SHELL`,
tmux, and anything that shells out) — do not silently bundle it in.

**The repo already knows this hazard.** The `gnu-tools` topic puts Homebrew's
GNU coreutils on `PATH` ahead of BSD tools for exactly this reason (its
`files/zsh/executable_path.zsh` prepends `libexec/gnubin`). A bash topic is the
same shape, and `apps/mise`'s `topic_provides` list is the precedent for
declaring what a topic supplies to other topics.

**Scope boundary.** This is configuration, not a build: install a package via
the owning package manager, place it in `PATH`, declare the provision. If it
turns out to need a bespoke shim or a rewritten bootstrap, stop and say so —
per `AGENTS.md` § What agents do here.

**Machine granularity, asked first.** Which machines need this:
`ansible_facts['os_family'] == 'Darwin'` needs it (that is where 3.2 lives).
Linux distros ship bash 5.x, so a Debian leg would be `absent`-or-skip rather
than an install — and the topic must not declare `homebrew` in
`topic_requires` or it becomes unschedulable on Linux (`AGENTS.md`
§ Cross-platform gives `apps/ollama/topic.yml` as the pattern).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A `bash` topic exists under `home/dotfiles/apps/bash/` with `topic.yml`, following `docs/TOPICS.md`
- [ ] #2 On Darwin the Homebrew bash is installed by the topic, not only by the standalone bootstrap script, and the installed version is reported — not assumed to be modern
- [ ] #3 `/opt/homebrew/bin` precedes `/bin` for a non-interactive shell, proven by asking a fresh non-login shell which bash it resolves, rather than by reading a config file
- [ ] #4 The topic does not declare `homebrew` in `topic_requires`, so it stays schedulable on Linux where the package manager differs
- [ ] #5 `--tags remove` tears down what the topic created, per the lifecycle rule that every created state has a matching teardown
- [ ] #6 The login shell is either deliberately left alone, or changed in a separate commit with its blast radius stated — never bundled into this one
- [ ] #7 `brew-bootstrap`'s duplicate `brew install bash` is reconciled: either it defers to the topic or the two are shown not to conflict, and the outcome is recorded
- [ ] #8 The version floor the 36 `#!/usr/bin/env bash` scripts actually need is stated, with the bash 3.2 failure that motivated this cited as the evidence
<!-- AC:END -->

## Implementation Notes
<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Read first: `docs/TOPICS.md` (topic structure, `topic.yml` schema, tiers,
lifecycle tags), `AGENTS.md` § What agents do here and § Cross-platform, and
PR #148 (DOT-303/DOT-309) for the bash 3.2 failure that prompted this.

The concrete failure to test against, from `scripts/run-molecule.sh` in PR
#148 before commit `ba2be76`:

```sh
set -u
arr=()
printf '%s' "${arr[@]}"      # bash 3.2: unbound variable
```

That is the reproduction. Confirm it on a real 3.2 if one is reachable, and
record which construct was used — the fix for the wrapper was to branch, which
is correct for a script that must survive any shell, but does not make 3.2 a
supported target for the other 35.

`/etc/shells` is **not** required for the `env bash` scripts, only for
`chsh`. Do not add it as a side effect of this task without saying so, because
it writes outside the user's home.

Check whether `apps/homebrew/tasks/prerequisites.yaml` is the right home for
the install instead of a new topic — a bash topic that duplicates one line of
an existing task is worse than adding the line. Decide with reasoning recorded
either way; the topic is right if bash needs its own lifecycle beyond a package
name.

Related: DOT-323 (macOS VM cleanup — it hit this same 3.2 trap and worked
around the shell rather than fixing it); DOT-248 (bash syntax convention in
.zsh files).
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A fresh Mac that runs the repo's provisioning resolves `bash` to Homebrew's build for non-interactive scripts, without running the standalone bootstrap first
<!-- DOD:END -->
