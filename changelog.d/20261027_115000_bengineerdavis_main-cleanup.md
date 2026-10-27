**Changed**

- The agent temp root is allowed outside the project: `~/.cache/tmp` for
  handoff documents and scratch files. `/tmp` is not allowed; the access that
  once needed it came from running mise under sudo, which the shell and
  Ansible guards refuse.
- `npm:@sentry/dotagents` is pinned to `3.3.0` rather than `latest`, so the
  binary the dotagents topic calls is the one the machine has. `latest` left
  the pin implicit and let 3.4.0 arrive through a separate `npx` channel.
- `github:danielmiessler/fabric` is bumped to `1.4.516` while upstream's
  version-prefix handling is checked. The duplicate-tree failure in the comment
  was measured at `1.4.478`.
