# Topic conventions

This document codifies the conventions every topic in `apps/` must follow,
and the contract between topics and the parent `playbook.yaml`.

## Topic structure

A topic is a self-contained Ansible role under `apps/<topic>/`. Required files:

- `topic.yml`           — topic metadata (at role root)
- `CHANGELOG.md`        — this topic's own history (see below)
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

## Shared guards (`roles/guards`)

A guard is a check that runs **before** a topic changes anything and fails with
the fix named when the machine is not in a state the topic can act on. Two live
inside the topic that needs them — `apps/chrome/tasks/git-refs-guard.yaml`,
`apps/rancher-desktop/tasks/path-management.yaml` — because only that topic
needs them. A check more than one topic needs goes in `roles/guards` rather than
being copied into each.

Call one with a static `import_role` and `tasks_from`:

```yaml
- name: "Guard against an unmigratable agent skills directory"
  ansible.builtin.import_role:
    name: "roles/guards"
    tasks_from: dotagents-skills-migration.yaml
  vars:
    guard_caller: "apps/<topic>"
    guard_allow_skill_dir_conflicts: "{{ <topic>_allow_skill_dir_conflicts }}"
```

`import_role`, not `include_role`: the import is static, so the guard's own tasks
are visible at parse time and the lifecycle tags in `tasks/main.yaml` keep
selecting them without an `apply:` block. `tasks_from` is Ansible's built-in way
to call one file from a role, and `roles/guards/defaults/main.yaml` gives every
parameter a default so a caller overrides only what it cares about.

The role name is the path `roles/guards`, matching how the parent playbook
already names topics (`include_role: name: "apps/{{ item.topic_name }}"`). Both
resolve relative to the working directory — the same constraint `ansible.cfg`
itself is under, and one `run-role.sh` and `update.sh` already satisfy.

Guards live in `roles/`, not `apps/`. `apps/` means topics: the parent playbook
discovers them by `topic.yml`, `topic_tier` orders them, and the CRUD ownership
invariant applies to them. A guard has no lifecycle and creates no state.

Rules for writing one — the longer version is in `roles/guards/README.md`:

- **Collect every problem, then fail once**, exactly as § Script dependency
  guards requires of `~/bin`. One run reports all of it, not one item per
  invocation.
- **Never repair automatically.** A guard exists because the right answer needs a
  human. Offer a per-run `_allow_` override defaulted to `false` instead.
- **Say what has not happened yet.** "Nothing has been installed or moved" tells
  the operator the run stopped clean rather than part-way through.
- **Prefix parameters `guard_`** so a caller's `vars:` cannot collide with the
  topic's own variables.

## Fully qualified module names

Use fully qualified collection names (FQCNs) for every module. A bare `apt` or
`homebrew` resolves through Ansible's search path, which means the module a task
runs can change with the installed collections rather than with the task.

```yaml
# ✅
ansible.builtin.apt
community.general.homebrew
community.general.homebrew_cask
community.docker.docker_image

# ❌
apt
homebrew
```

## Presence vs currency — install and upgrade are different questions

Two separate guarantees, and a topic needs both covered:

| | Question | Tag | Mechanism |
|---|---|---|---|
| **Presence** | is it installed at all? | `install` | modules with `state: present` |
| **Currency** | is it the latest version? | `upgrade` | the system role's `upgrade_all`, or the topic's own upgrade tasks |

`state: present` converges: it installs what is missing and is a no-op on what is
already there. It deliberately does **not** upgrade — that is `state: latest`,
which is not used here, because it would couple presence to currency and make
every install pass hit the network.

The consequence is that neither tag alone covers both. `--tags install` adds what
is missing and leaves versions alone; `--tags upgrade` refreshes what exists and
never installs anything absent. **A run that must guarantee both asks for both:**
`--tags "install,upgrade"`. That is the closest thing to a converge operation, and
it is also why `./update` — which requests `upgrade` only — cannot install a topic
that was never provisioned.

### Currency for anything brew and apt do not install

"Upgrade logic belongs in system roles" holds only for packages a system role
actually manages. A topic installed some other way is **not** reached by the
system upgrade pass, so it must own its own upgrade or it silently never updates.

Both current cases do this deliberately: `apps/ori` fetches a release binary and
`apps/ollama` unpacks a tarball, and each tags its install tasks
`[install, upgrade]` so the same checksum-compared fetch serves both phases. That
is not a violation of the rule below — it is the case the rule does not cover.

The test for a new topic: *if `brew upgrade` / `apt upgrade` will not move this to
the latest version, what will?* If the answer is nothing, the topic is missing its
upgrade path.

## Where upgrade logic lives

Upgrade logic for **brew- and apt-installed packages** belongs in system roles
(`homebrew`, `apt`, `docker`), not in topics.
If you find that kind of upgrade task in a topic's `install.yaml`, move it to the
system role. For topics the system roles cannot reach, see the section above.

```yaml
# ❌ wrong — upgrade logic in a topic
- name: "Update Homebrew"
  community.general.homebrew:
    update_homebrew: true

# ✅ correct — topic only installs
- name: "Install my-app via Homebrew"
  community.general.homebrew:
    name: my-app
    state: present
  when: ansible_facts['os_family'] == 'Darwin'
```

## Adding a System Role

System roles (`homebrew`, `apt`, `docker`) follow the same topic structure  
but include additional subtasks. When adding a new package manager:

1. Create `apps/<pm>/` using `init-config.sh <pm>`
2. Add `tasks/bootstrap.yaml` — existence check + confirmed install
3. Add `tasks/prerequisites.yaml` — core tools, idempotent
4. Add `tasks/upgrade.yaml` — system-wide upgrade
5. Update `tasks/main.yaml` to import all five subtasks with correct tags
6. Add the new system role to the parent `playbook.yaml` bootstrap/prerequisites/upgrade sequence
7. Add it to `SYSTEM_ROLES` in `migrate-to-roles.sh`

Bootstrap tasks must:
- Use an explicit `stat` check — never rely on module idempotency alone
- Prompt for confirmation before installing
- Verify success after installing
- Fail loudly if something goes wrong

## Per-topic changelog and local edge cases

Every topic keeps its own `CHANGELOG.md`, and anything surprising about *that*
topic is recorded in the topic — in its changelog, its README, or in a comment
beside the task that works around it. Not in a central document.

This is a portability rule, not a bookkeeping one. `PRD.md` § "Topics are
installable modules" wants someone to borrow one topic without adopting the
repository; `ROADMAP.md` carries the unsettled boundary. A topic that keeps its
history and its quirks somewhere else arrives at its new home stripped of both,
and the first person to hit a known edge case rediscovers it from scratch. Same
reasoning as co-locating a topic's tests: what travels with the directory is what
survives the move.

The root `CHANGELOG.md` is unaffected — it answers "what changed in this repo",
which is a different question from "what has this topic done to me".

### Categories

Use the section names from **antsibull-changelog** — the Ansible community's
changelog tool. It is spelled *antsibull*, which is the project's real name and
not a typo for *ansible*.

    release_summary      short prose; a single string, not a list
    breaking_changes     needs user action on upgrade
    major_changes        large changes across several tasks
    minor_changes        a new option, a new behaviour
    deprecated_features  on the way out
    removed_features     gone, deprecated earlier
    security_fixes       security-relevant, with CVE where there is one
    bugfixes             everything else that was broken
    known_issues         not fixed, or will not be fixed
    trivial              too minor to surface

Borrowed rather than invented for one reason: if topics ever become a real
Ansible collection, `changelogs/changelog.yaml` is the format the ecosystem
already generates and consumes, and matching category names makes that a
conversion instead of a rewrite. Nothing here depends on the tool being
installed — these are section headings in a Markdown file.

**`known_issues` is where topic-specific edge cases go.** Upstream behaviour we
cannot change, a workaround whose reason is not obvious from the code, a failure
whose error message names neither the cause nor the fix. Where the workaround
lives in a task, the task carries the comment and the changelog carries the
entry — the comment survives a rebase, the entry survives a move to another repo.

Entries are dated, not versioned: topics carry no version yet, and inventing one
per topic would be a versioning scheme nothing consumes.

## Template Conformance

`template_dir/` is the canonical structure. `init-config.sh` copies it verbatim.  
`migrate-to-roles.sh` uses it as the reference for LLM conformance checks.

If you change the canonical structure, update `template_dir/` first,  
then run `migrate-to-roles.sh` to propagate changes to existing topics.

Do not add `tasks/bootstrap.yaml` or `tasks/prerequisites.yaml` to `template_dir/` —  
those are system-role-only files.

## Commit granularity

Moved. Commit conventions live in the root **`CONTRIBUTING.md`** — they are not
topic conventions, and this document is about topics.

The `commit-hygiene` skill is the agent-facing form of the same rules and
references that file rather than restating it.

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

Keep a topic self-contained: install and system state in `tasks/`, shell wiring
in `files/zsh/*.zsh`, metadata in `topic.yml`.

Verify without changing anything before you commit:

```bash
ansible-playbook apps/<topic>/playbook.yaml --syntax-check
ansible-playbook apps/<topic>/playbook.yaml --check --tags provision
```

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
