# Topic conventions

This document codifies the conventions every topic in `apps/` must follow,
and the contract between topics and the parent `playbook.yaml`.

## Topic structure

A topic is a self-contained Ansible role under `apps/<topic>/`. Required files:

- `topic.yml`           — topic metadata (at role root)
- `tasks/main.yaml`     — lifecycle router (see below)
- `tasks/bootstrap.yaml`     — bring the system tool into existence on a fresh machine
- `tasks/prerequisites.yaml` — core dependencies needed before any topic installs
- `tasks/upgrade.yaml`  — upgrade steps (no-op for app-tier topics)
- `tasks/install.yaml`  — install steps
- `tasks/remove.yaml`   — teardown steps

App-tier topics typically leave `bootstrap.yaml`, `prerequisites.yaml`, and
`upgrade.yaml` as no-op stubs — `brew`/`apt` cover them at tier 0.

The `meta/` directory is reserved for Ansible/Galaxy use. Our metadata lives
at the role root (`topic.yml`) so it does not collide with Ansible's strict
validation of `topic.yml`.

## topic.yml schema

```yaml
topic_name: <string>           # canonical name; must match directory
topic_provides: [<string>...]  # package managers/registries this topic provides;
                               # empty list for app-tier topics
topic_requires: [<string>...]  # package managers this topic depends on at
                               # install / upgrade time
topic_os: [<string>...]        # OS families this topic supports: Darwin, Debian
topic_tier: <pkg-manager|runtime-manager|app>
```

The parent playbook reads every topic's `topic.yml` on every run. These keys
are this project's convention. We deliberately do not use `topic.yml`
because Ansible's role loader validates that file strictly and rejects
unknown top-level keys.

## Tiers

Topics are ordered by tier during execution:

| Tier              | Purpose                                                | Examples                    |
|-------------------|--------------------------------------------------------|-----------------------------|
| `pkg-manager`     | Foundational system installer                          | `apt`, `homebrew`, `docker` |
| `runtime-manager` | Manages a subordinate set of versioned tools/models    | `mise`, `ollama`            |
| `app`             | Normal application; no subordinate state of its own    | everything else             |

Within a tier, topics run in alphabetic order.

## Lifecycle tags

Every topic's `tasks/main.yaml` is a router that imports the lifecycle files
with the following tags:

| Tag             | Imports                          | When it runs                                 |
|-----------------|----------------------------------|----------------------------------------------|
| `bootstrap`     | `bootstrap.yaml`                 | first-time setup of a system tool            |
| `prerequisites` | `prerequisites.yaml`             | core deps before topics install              |
| `upgrade`       | `upgrade.yaml`                   | refresh installed state                      |
| `install`       | `install.yaml`                   | install the topic                            |
| `remove`        | `remove.yaml`                    | explicit uninstall; tagged `never` — runs **only** with `--tags remove` |
| `provision`     | bootstrap + prerequisites + upgrade + install | full fresh-machine setup        |

`--tags upgrade` against the parent playbook runs every topic's upgrade step
in tier order. Running a single topic's standalone playbook with
`--tags upgrade` upgrades just that topic.

The `remove` import is tagged `[remove, never]`. Ansible's `never` tag means a
task is skipped by every invocation *except* one that explicitly requests it,
so `remove` runs only under `--tags remove`. This makes bare runs safe: a
plain `ansible-playbook apps/<topic>/playbook.yaml` (no tags) runs `provision`
and never tears the topic down. Uninstalling is always a deliberate
`--tags remove`; new topics inherit this from `template_dir`.

## Dependency resolution

The parent playbook reads every `topic.yml`, builds a
`provides_map = {provided_name: topic_name}`, and resolves each topic's
`topic_requires` against three diagnostic states:

| State           | Meaning                                                                                       | Result   |
|-----------------|-----------------------------------------------------------------------------------------------|----------|
| `OK`            | Dep is provided by a topic in the run, or is on PATH                                          | silent   |
| `TOPIC_NOT_RUN` | A topic in the repo provides this dep, but it is not in the current run and not yet installed | fail (warn under `remove`) |
| `NO_TOPIC`      | No topic provides this dep, and it is not on PATH                                              | fail (warn under `remove`) |

The check distinguishes the two failure modes explicitly so operators have a
clear next action:

- `TOPIC_NOT_RUN` → re-run with `--tags provision` or install the providing
  topic first.
- `NO_TOPIC` → either add a topic for the dependency, or remove the
  requirement from the calling topic's `topic.yml`.

The check fails under `bootstrap`, `prerequisites`, `install`, `upgrade`, and
`provision`. It warns-but-continues under `remove`, since you may be tearing
down the very tool the requirement was satisfied by.

## Shared dependencies

`provides_map` answers *"which topic installs X"*. Teardown needs the opposite
question — *"who still needs X"* — so the parent playbook also builds a reverse
index:

```yaml
requires_map = {dep_name: [topic_name, ...]}   # every topic requiring dep_name
```

Any dep with more than one consumer is reported at run start as a
`[shared-dep]` line naming the topics involved.

`requires_map` is built from **every** topic in `apps/`, not just the topics in
the current run. A topic excluded by `topic_os` is still a consumer; only a dep
that no topic anywhere claims is safe to uninstall.

**A topic must not uninstall a dependency another topic requires.** Where the
CRUD invariant below says a topic tears down what it created, this is the
exception that makes teardown safe for shared *system* packages. A teardown of
a shared dep consults `requires_map` and skips if anyone else claims it — see
`apps/mise/tasks/remove.yaml`, which owns `ffmpeg` for `llm-video-frames`:

```yaml
- name: "Remove: find other topics that require ffmpeg"
  ansible.builtin.set_fact:
    mise_ffmpeg_consumers: >-
      {{ (requires_map | default({})).get('ffmpeg', [])
         | reject('equalto', 'mise') | list }}
```

Two rules for writing one of these:

- **Fail safe when the index is absent.** `run-role.sh` invokes a topic's
  standalone playbook, which skips the parent's `pre_tasks`, so `requires_map`
  is undefined there. Undefined means *unproven*, not *unshared* — skip the
  removal rather than assume it is harmless.
- **Make it opt-in as well.** The index only proves no *topic* claims the dep;
  it cannot know what the human installed by hand. Pair the check with a
  `<topic>_remove_<dep>` default of `false`.

To declare a shared system dependency: the owning topic lists it in
`topic_provides` (so it resolves for everyone else), and each consumer lists it
in `topic_requires`. That is what populates both maps.

## Script dependency guards (`~/bin`)

**Every standalone script checks every dependency it shells out to, before
doing any work.** Both kinds count:

| Kind            | Examples                        | Arrives via              |
|-----------------|---------------------------------|--------------------------|
| system tool     | `llm`, `ollama`, `ffmpeg`, `jq` | an Ansible topic         |
| user script     | `llm-ctx`, `brew-init`          | `chezmoi apply ~/bin`    |

Being topic-managed is **not** grounds for skipping a check. It only means
something *should* have installed the dependency, which is exactly the
assumption that breaks on a fresh, half-applied, or non-provisioned machine —
and a standalone script is by definition one that may run there. A guard costs
one `command -v` and converts a confusing downstream failure into a named
missing dependency.

The guard is a `require` function — `command -v` in bash, `shutil.which` in
Python — that collects **all** missing names before failing, so one run reports
every gap rather than one per invocation. It exits **127**, the conventional
"command not found" status, and runs before any file is opened for writing:

```bash
require() {
    local missing=() cmd
    for cmd in "$@"; do
        command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
    done
    if ((${#missing[@]})); then
        printf '%s: missing dependencies: %s\n' "${0##*/}" "${missing[*]}" >&2
        exit 127
    fi
}

require llm-ctx
```

Order matters: a guard that runs after `> "$OUTPUT_FILE"` has already truncated
the output, and a script that reports a missing dependency but exits 0 (as
`bin/mailbox` once did) looks like a success to everything calling it.

Conditional dependencies are checked at the point the feature is used, not up
front — `bin/llm-ctx` checks `ffmpeg` only once a video has actually matched, so
an ffmpeg-less machine stays perfectly usable for text and images.

## Commit granularity

One commit should be one reviewable decision. The test is not file count or diff size —
it is whether a reader can hold the *why* in their head, and whether the change can be
reverted on its own without taking unrelated work with it.

Two failure modes, and the repo has an example of each.

**Too coarse.** `491c9ca "fetchurl: download what it finds by default, with live parallel
progress"` touched one file, so it looked atomic, but it bundled four independent
decisions: a stray-character fix in the shebang, a change to what a positional argument
means, a new progress display, and two new pipeline flags. Reverting the progress bars
there means reverting the CLI contract too. The message had to spend five paragraphs
because it was narrating four stories.

**Right-sized.** The Debian port of `apps/clamav` landed as five commits —
`--config-file` plumbing, per-platform path resolution, the netcat dependency, apt
install, the systemd timer, then flipping `topic_os`. Each is independently revertible and
each subject line is a complete thought. That is the shape to aim for.

### Where to draw the line

| Split when | Keep together when |
|---|---|
| A reader would ask "why is this here?" about part of the diff | The parts are meaningless alone — a flag and the code reading it |
| One part could be reverted while keeping the rest | Splitting would leave a commit that does not run or test green |
| The subject line needs "and" | The change is one decision expressed in several files |
| A drive-by fix rode along with a feature | A rename or signature change touching many call sites |

Do **not** split to the point where commits cannot stand alone. A commit that leaves the
tree broken so the next one can fix it is worse than a slightly coarse one: it breaks
`git bisect`, and it makes every intermediate state a lie. Atomic means *self-contained*,
not *small*.

### Messages

Subject: `scope: imperative statement`, lower case after the colon, no trailing period,
under ~72 characters. Scope is the topic or script the change belongs to (`clamav:`,
`fetchurl:`, `docs:`, `tests:`).

The body explains **why**, not what — the diff already says what. Worth the words:
measurements that justify a choice, the failure the change prevents, an option considered
and rejected, and any blind spot knowingly accepted. Those are the things a reader cannot
reconstruct from the code, and they are the reason the body exists at all.

If the body is enumerating unrelated changes rather than explaining one, that is the
signal to go back and split.

## CRUD ownership invariant

**Any state a topic creates in `bootstrap.yaml`, `prerequisites.yaml`,
`install.yaml`, or `upgrade.yaml` must have a matching teardown in
`remove.yaml`.**

Non-topic dependencies — launchd plists, completion files, PATH edits,
downloaded archives, dot-directories — belong to the topic that introduced
them. They do not leak across topics. If a side effect is shared by two
topics, either promote it to its own topic, or own it explicitly in the
topic upstream of both.

The parent playbook cannot enforce this. It is a contributor rule, caught
in review.

## Adding a new topic

```bash
./init-config.sh my-topic
```

This scaffolds `apps/my-topic/` from `template_dir/`. Edit:

1. `apps/my-topic/meta/main.yml` — fill in `topic_name`, `topic_tier`,
   `topic_requires`, `topic_os`.
2. `apps/my-topic/tasks/install.yaml` — install steps.
3. `apps/my-topic/tasks/remove.yaml` — matching teardown.
4. `apps/my-topic/tasks/upgrade.yaml` — leave empty for app tier; fill in for
   runtime-manager or pkg-manager tiers.

The parent playbook picks up the new topic automatically on next run.
