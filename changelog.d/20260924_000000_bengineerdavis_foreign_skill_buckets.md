**Added**

- `skill-trust` recognises a foreign skill bucket — another program's directory
  in the skills store, like Claude Code's `synced/` — as `external` rather than
  denying it. Detection is by evidence (the path, a `.bucket-<id>` marker, and a
  `manifest.json` with a `skills[]` array), and a `deny` on such a bucket is
  refused with the reason rather than attempted. `foreign_buckets: false`
  restores the old fail-closed denial.

**Fixed**

- Provisioning no longer fails outright when Claude Code's cloud-synced skills
  are present: the approved-sources guard now recognises that bucket as out of
  its jurisdiction, and runs as the last task in `apps/opencode` so one
  offending skill cannot block the rest of the install.