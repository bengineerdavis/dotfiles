**Fixed**

- The dependency check failed for `opencode` — and would fail for any topic
  requiring `homebrew` — on a Debian box running linuxbrew: it probed for a
  `homebrew` binary, but Homebrew's CLI is `brew` on every platform, so the
  check reported `[TOPIC_NOT_RUN]` for a dependency that was present. The
  resolver now maps the `homebrew` token to the `brew` binary
  (`roles/topic-resolution/defaults/main.yaml`), so the requirement resolves
  via the `apps/homebrew` topic on macOS and via linuxbrew on the PATH on
  Debian.

**Changed**

- Dependency resolution moved out of `playbook.yaml` pre_tasks into a shared
  `roles/topic-resolution` role, so it is tested under both OS families rather
  than only observed on whichever machine last provisioned. Behaviour is
  unchanged: the same facts are emitted and the same three states
  (`OK` / `TOPIC_NOT_RUN` / `NO_TOPIC`) are enforced.