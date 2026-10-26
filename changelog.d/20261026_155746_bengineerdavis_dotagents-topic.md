**Added**

- `apps/dotagents`: a new topic that owns the machine's global agent-artifact
  declaration — the approved source list, the source-trust allow-list, the
  per-source excludes, the vendored-skill exceptions, and the sync that
  installs them. It calls the mise-pinned `dotagents` binary rather than
  `npx @sentry/dotagents@latest`, so one version exists on the machine.

**Changed**

- The global skill declaration moved out of `apps/opencode`. That topic keeps
  the binary and config and no longer carries a skill manifest, and `node` is
  no longer one of its dependencies.
- The provenance guard runs from `apps/dotagents`, still last in the install,
  and receives that topic's source and vendored lists.

**Known issues**

- `dotagents init --force` deletes the skills store (measured 2026-10-26), so
  init runs only when `agents.toml` is absent. Changing the agent list later is
  a deliberate destructive act.
- A fresh `init` installs a `dotagents` skill from an untrusted source; install
  removes it immediately so the provenance guard does not fail on it.
