# ollama — changelog

## 2026-09-23

### bugfixes

- The ollama server is restarted when an upgrade leaves it running the old
  binary. On macOS, `apps/homebrew` upgrades the formula in an earlier tier,
  and until now nothing restarted `com.ollama.server`. On 2026-09-22 it ran
  0.33.3 for hours after 0.34.3 was installed. The end of `tasks/install.yaml`
  now calls `roles/restart-stale` under `--tags install` and `--tags upgrade`.
  It restarts the agent only if the agent started before the binary's ctime.
  On Debian it checks the system `ollama` unit.

### known_issues

- On Debian, the per-GPU instances (`ollama_linux_instances_enabled`) are not
  checked for staleness. The topic restarts them itself whenever it swaps the
  tarball. A swap made some other way leaves them on the old binary.
- `launchctl kickstart -k` probably stops the server with SIGKILL rather than
  SIGTERM. The man page says only "kill the running instance". After the
  manual `kickstart -k` on 2026-09-22, `launchctl list com.ollama.server`
  reported `LastExitStatus = 9`, which is consistent with SIGKILL but does not
  prove it. Loaded models reload on demand, so nothing persistent is lost.
