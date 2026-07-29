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
