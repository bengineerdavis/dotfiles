# Contributing

Rules, patterns, and what goes where.

## The contract

Every topic must follow the conventions in **[CONVENTIONS.md](CONVENTIONS.md)** —
topic structure, the `topic.yml` schema, tiers, lifecycle tags, dependency
resolution, and the CRUD-ownership invariant. That document is the source of
truth; this page is just the workflow around it.

New to the repo? Start with [ARCHITECTURE.md](ARCHITECTURE.md) for the big
picture and [USAGE.md](USAGE.md) for the commands.

## Adding or changing a topic

- Scaffold with `./init-config.sh <name>` — never hand-roll the layout. The
  template ships all five lifecycle files plus a router that already tags
  `remove` as `[remove, never]`.
- Keep a topic self-contained: install/system state in `tasks/`, shell wiring in
  `files/zsh/*.zsh`, metadata in `topic.yml`.
- **Anything you create in `bootstrap`/`prerequisites`/`install`/`upgrade` must
  have a matching teardown in `remove.yaml`.** (CRUD invariant.)
- Gate OS-specific work with `topic_os` and `when: ansible_facts['os_family']`.
- Verify without changing anything before you commit:
  ```bash
  ansible-playbook apps/<topic>/playbook.yaml --syntax-check
  ansible-playbook apps/<topic>/playbook.yaml --check --tags provision
  ```

## Commits

- One concern per commit.
- Subject: `<scope>: <imperative summary>` — `scope` is the topic name or area
  (`docker`, `mise`, `playbooks`, `docs`, `template_dir`, `chezmoi`). Lowercase,
  concise, present tense. Body explains *why* when it isn't obvious.
- Examples: `docker: capture Debian-only topic.yml`, `docs: fix broken README
  links`, `template_dir: scaffold remove as opt-in (never tag)`.

## Before you push

Git hooks (shellcheck + BATS, via [prek](https://github.com/azer/prek)) run on
staged shell scripts under `bin/` and `scripts/` at pre-commit and pre-push. Run
them yourself first:

```bash
bats test/               # full shell-script test suite
```

Convention: a script `<subdir>/foo.sh` is tested by `tests/foo.bats`; scripts
with no matching test are flagged by the runner.
