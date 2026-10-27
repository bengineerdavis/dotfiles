### Changed

- loreai: the opencode extension task now verifies the plugin is installed
  and loading, not merely registered in the deployed config. Measured
  2026-10-27: the config listed `@loreai/opencode` while the shared
  server's in-process auto-install failed for hours (protocol errors,
  then lock-timeout collisions, in the opencode server log), and once
  installed via `opencode plugin add` the loader still rejected 0.40.0's
  pre-v2 function-shaped default export — so a config grep reported a
  working gateway that was not there. The task now reads `opencode plugin
  list` and the server log, and names the fix per state: manual
  `plugin add` plus `opencode service restart`, or an upstream BYK/loreai
  release for the load rejection.
- loreai: registered-but-broken opencode plugin states now raise instead of
  whispering in a debug line — a wedged auto-install fails the run (the fix
  is two local commands), and a loader rejection of a pre-v2 plugin export
  raises red without blocking the playbook (`ignore_errors`; recap
  ignored=1). Verified live under `--check`: the loader rejection surfaces
  as FAILED!/ignored=1 while the rest of the topic stays green.
