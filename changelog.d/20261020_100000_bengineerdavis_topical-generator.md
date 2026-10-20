# Added

- `topical new` — a manager-aware topic generator in `tools/topical/`.
  Scaffolding a topic now fills `topic.yml` from flags and emits only the
  install/remove blocks the declared package managers need, reading
  `dotfiles/managers.yaml`, instead of copying a five-way commented menu
  and leaving every field to hand-editing. `apps/firefox` was regenerated
  with it and its hand-maintained playbook came out byte-identical to the
  generated one.

# Removed

- Twenty dead topic-root files nothing loaded: twelve `tasks.yaml` with
  unedited template boilerplate, three whose install task duplicated the
  lifecycle install, and five `main.yaml` leftovers.
