# AGENTS.md

Instructions for coding agents working in this repository. Human-facing detail lives
in `docs/` — this file links there rather than restating it, so the two cannot drift.

## What this repo is

A chezmoi-managed dotfiles repo with an Ansible layer for system state. Read
`docs/ARCHITECTURE.md` first; `docs/CONTRIBUTING.md` has the layering rules that
govern where a change belongs.

The one rule worth repeating here because it is the most common mistake: **one
concern per layer.** chezmoi owns dotfiles and symlinks, Ansible owns package
installs and system state, zsh owns shell runtime config. A symlink task in Ansible
belongs in chezmoi; a `brew install` in a shell script belongs in Ansible.

## Where the source of truth is

Scripts under `bin/` are **chezmoi source files**, named `executable_<name>`. The
deployed copy at `~/bin/<name>` is what actually runs. They drift, in both
directions:

```bash
chezmoi status                 # what differs
chezmoi add ~/bin/<name>       # deployed  -> source   (adopt a hand-edit)
chezmoi apply ~/bin/<name>     # source    -> deployed  (push a repo change)
```

Before editing a `bin/` script, check `chezmoi status`. Committing the source while
the deployed copy is ahead silently reverts the working version on the next
`chezmoi apply`.

## Commands

```bash
# Tests — pytest is primary. Needs these three or most of the suite silently skips.
uv run --with pytest --with hypothesis --with typer --with questionary pytest tests -q
uv run --with pytest pytest tests -m "not llm_judge" -q   # skip real-model tests
uv run --with pytest pytest tests -m llm_judge -q         # only real-model tests

bats tests/<name>.bats         # bash scripts only — see Languages below
./run-role.sh <topic>          # apply one ansible topic
./run-role.sh <topic> remove   # tear it down
```

A bare `pytest tests` reports "24 passed, 89 skipped" and looks green while testing
almost nothing — the `binned_module` fixture skips without `typer`/`questionary`.

## Commits

Commit messages here got long because commits were doing too much, not because the
messages were verbose. The length was the symptom. Fix the granularity and the
message shrinks on its own.

**One logical change per commit.** Logical, not physical — the test is not "how many
files" but three questions:

- **Atomic** — does the tree work before and after? A commit that leaves a template
  referencing a task that does not exist yet is not atomic.
- **Revertable alone** — can this be reverted without untangling something else?
- **Reviewable** — can a reader hold the whole change in their head?

Subject line: `topic: what changed`, imperative, under ~72 characters. Body: why,
and only what a reverter needs. Under ~10 lines. Durable *why* belongs in a code
comment next to the decision, where it survives rebases and is read by people who
never look at git log.

### A list of changes is a list of commits

If the body needs bullets to enumerate what changed, that is the signal. But
enumeration is only a signal, not a rule — these are **not** splits:

| Looks like a list | Actually one commit |
|---|---|
| The same mechanical change across 40 files | One commit. A list of *files* is not a list of *concerns*, and splitting by file breaks atomicity mid-way. |
| A feature whose pieces are individually dead | One commit. A systemd unit template plus the task that installs it: template alone is dead code, task alone references a missing file. |
| "Verified X, Y and Z" | One commit. That is a list of checks, not of changes. |
| A rename plus its call sites | One commit. Splitting leaves the tree broken. |

And the inverse — these look like one change but are several:

- **A cross-platform change that also alters existing behaviour.** Adding Linux
  support while changing what macOS does is two commits, or the macOS fix cannot be
  reverted without losing Linux support.
- **A refactor bundled with a behaviour change.** Always separate. A reviewer cannot
  tell which lines were meant to change behaviour.
- **A fix plus the unrelated cleanup you noticed while there.**

### Ordering

Sequence commits so every intermediate state works. Land the inert parts first and
the switch that activates them last — for an Ansible topic that is usually
`topic_os`, which gates whether any of the preceding commits run at all. That
ordering makes `git bisect` meaningful and lets the enabling commit be reverted on
its own to turn a feature off without unpicking the implementation.

### Worked example

`clamav: extend the topic to Debian/Ubuntu` was one commit, 9 files, 33 lines of
body. It became six, and splitting it surfaced a bug the single commit had hidden: a
new `clamav_clamd_conf` var collided with an existing `register:` of the same name,
and registered vars outrank role vars — so the rendered script would have received a
task-result dict instead of a path. Reading each change in isolation is what caught
it.

```
clamav: pass --config-file to every clamav binary            # behaviour, both platforms
clamav: resolve config, database and binary paths per platform
clamav: install netcat-openbsd and verify nc -U on Debian    # independent trap
clamav: install via apt, without the always-on daemon
clamav: schedule the daily scan with a systemd user timer on Debian
clamav: enable the topic on Debian                           # the switch
```

## Languages

**Bash while a script is small; Python once it is not.** Short bash needs nothing
but a shell, which is why it wins for small jobs. Past roughly 80–100 lines that
trade stops paying: argument parsing, temp files and error paths are where bash gets
verbose and subtly wrong.

Count lines of **logic**, not lines of file. A script that is mostly an interface to
other programs does not qualify however long it is — `bin/findline` is 256 code
lines that pipe `rg` into `fzf` with a `bat` preview, so all the behaviour and all
the speed live in three Rust binaries. Porting it would add interpreter startup to
an interactive tool and make it worse. Its header records this so the question is
not reopened. Contrast `bin/clipped`: similar size, but genuinely branchy platform
dispatch, and worth porting.

Stdlib-only Python needs no dependency block — use `#!/usr/bin/env python3` like
`bin/mailbox`. Reach for `#!/usr/bin/env -S uv run --script` with inline PEP 723
deps only when third-party packages are genuinely needed, as `bin/llm-ctx` does.

`bin/binned` applies this rule to the scripts it generates: it counts effective
lines, recommends Python above 100, and asks a model in the 80–100 band.

## Tests

**pytest is primary.** Any Python script gets pytest tests. bats remains correct
only for scripts that are still bash (`bin/cleanup`).

When porting a script, keep its bats suite until the pytest suite is proven
equivalent — it tests the CLI as a black box, so it survives a language change
unaltered and is the safety net that proves the port. Then retire it.

Layout: `tests/<script>/conftest.py` plus `test_*.py` split by concern. Mark tests
that call real models with `llm_judge` so they stay out of the default run.

A port is a chance to test what bash could not. `default_output()` in
`bin/pii-redactor` was previously only reachable by running the whole CLI and seeing
which file appeared; called directly, the path edge cases became explicit. Platform
dispatch in `bin/clipped` could only be exercised by mocking `uname` on `PATH`, so
in practice only the host platform was ever tested.

Two harness traps found here, worth checking for in any suite you touch:

- A test path pointing at a file that does not exist. `tests/clipped.bats` used
  `$BATS_TEST_DIRNAME/../clipped` — the repo root — so every case ran against a
  missing binary, and the one case that "passed" did so because a nonexistent
  command also exits nonzero.
- GNU-only syntax in a portability test. `script -qec` is GNU; BSD `script` has no
  `-c`, so two TTY tests could never pass on macOS whatever the code did. Use
  `pty.openpty()`.

## Models

Local Ollama first, then Anthropic or Google **via `llm-openrouter`**. The `llm`
environment deliberately carries only `llm-openrouter` and `llm-ollama` for hosted
access, so vendor-native ids like `claude-opus-4.7` resolve to nothing — use
`openrouter/anthropic/claude-opus-4.7`.

No hosted GPT or Grok as a default, a recommendation, or a fallback. They are
legitimate as **benchmark subjects** — that is what `bin/model-bench` is for. The
line is hosted-vendor dependency, not the name: `gpt-oss:20b` is open-weights and
runs locally under Ollama, so it is welcome; `gpt-4o` is not.

Model ids must be the exact `ollama list` tag. What is pulled here are MLX and QAT
builds, so `qwen3.5:35b` does not exist but `qwen3.5:35b-mlx` does. Never match ids
by substring: `bin/binned` used to, so a bare `qwen3.5:35b` matched the installed
`-mlx` tag, passed the availability check, then failed at `llm -m` from inside a
judge panel.

**Do not invent ratings or benchmark numbers.** Quality claims must come from a
measured run. `bin/model-bench` scores judges on *calibration* against a reference
scorecard rather than on the scores they emit, because measuring raw magnitude
rewarded generosity — two local models awarded a flat 10/10 to a script with no
comments and an unguarded `--delete`, and outranked the model that caught it.

## Dependencies

Check every dependency a script shells out to, system tools and hand-rolled
`~/bin` scripts alike. Being topic-managed is not a reason to skip the check: it
only means something *should* have installed it, which is exactly the assumption
that breaks on a fresh or half-applied box. See `require()` in `bin/llm-ctx`.

Name the fix in the error, not just the failure: `~/bin` scripts come from
`chezmoi apply ~/bin`, system tools from the Ansible topics via `update.sh`.

## Cross-platform

macOS and Debian/Ubuntu are both targets. Guard the package manager in-task rather
than abstracting it — `docs/CONTRIBUTING.md` rule 2 has the pattern. A topic
supporting both should not declare `homebrew` in `topic_requires`, or it becomes
unschedulable on Linux; see `apps/ollama/topic.yml`.

Assume tools installed by uv or mise are identical across platforms. Only system
binaries need per-OS handling.

Traps that have actually bitten here:

- **A per-user launchd agent maps to a systemd *user* timer, not a system one.**
  Same ownership, no root. It only fires while the user has a session, so report the
  `loginctl enable-linger` fix rather than silently changing login behaviour.
- **`nc -U` needs `netcat-openbsd`.** Debian ships two providers and
  `netcat-traditional` has no `-U`; probe the `nc` on `PATH`, because alternatives
  can point at the wrong build.
- **BSD and GNU flags differ** for `script`, `stat`, `sed -i` and `mktemp`. Prefer
  Python over a portability shim, or try both forms.

## Verification

Prefer evidence over assertion, and say plainly what was and was not checked.

- Render Ansible templates under **both** `os_family` values and run `bash -n` over
  the result. Use Jinja's `StrictUndefined` — it catches missing variables that a
  permissive render silently leaves blank.
- Do not report a template or playbook as working on a platform it has not run on.
  Say it renders and was not yet applied there.
- When a background command's exit code matters, do not read it through a pipe:
  `| head` masks it.
- A model call that times out may just be a cold model load. Loading an 18 GB model
  can exceed a 120 s timeout, and the warmup timing out cascades into every
  subsequent run failing, which looks like a model problem and is not.
