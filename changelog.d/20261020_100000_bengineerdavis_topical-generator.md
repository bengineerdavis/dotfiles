# Added

- `topical new` — manager-aware topic scaffolding, living in its own repo
  at `~/code/personal/topical`. Scaffolding a topic now fills `topic.yml`
  from flags and emits only the install/remove blocks the declared package
  managers need, reading this repo's `dotfiles/managers.yaml` — instead of
  copying a five-way commented menu and leaving every field to
  hand-editing. `apps/firefox` was regenerated with it and is
  byte-identical to the generator's output.

# Removed

- `dotfiles/template_dir` and `init-config.sh` — the canonical topic
  skeleton moved to the topical repo, and `topical new` replaces the
  verbatim-copy scaffolder. The next `chezmoi apply` removes both from
  `~/dotfiles`.
- Twenty dead topic-root files nothing loaded: twelve `tasks.yaml` with
  unedited template boilerplate, three whose install task duplicated the
  lifecycle install, and five `main.yaml` leftovers.
