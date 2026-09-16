# roles/topic-resolution

Shared dependency resolution for the parent playbook.

The playbook discovers `apps/*/topic.yml` and hands that inventory to this role
with the target OS family. The role selects the topics that run, builds the
`provides`/`requires` maps, and resolves every `topic_requires` pair to one of
three states — `OK`, `TOPIC_NOT_RUN`, or `NO_TOPIC` — failing the run when a
dependency is unresolved.

It is a role, not inline pre_tasks, so `tests/topic_resolution/` can exercise it
under both OS families without running the whole play. The resolution is the
single place that decides whether `apps/opencode`'s `topic_requires: [homebrew]`
is satisfied: `homebrew` resolves via the `apps/homebrew` topic on Darwin, and
via the PATH probe for `brew` on Debian (see `dependency_probe_binary` in
`defaults/main.yaml`).

Inputs (required): `resolution_topic_metadata`, `resolution_os_family`.
Outputs (host facts, unchanged from the pre_tasks era): `topics_in_run`,
`provides_map_all`, `provides_map_run`, `requires_map`.