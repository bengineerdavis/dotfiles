**Fixed**

- The ollama server is restarted when an upgrade leaves it running the old
  binary. Until now, `brew upgrade` replaced the binary and
  `com.ollama.server` went on running the previous version until someone
  restarted it by hand. The new shared role `roles/restart-stale` restarts a
  service or app only if its process started before the binary's ctime.
  `apps/ollama` is its first caller.
