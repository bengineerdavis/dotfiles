### Fixed

- Close out the environmental suite failures (DOT-73). `clipped copy` no
  longer hangs callers on a daemonizing backend (xclip): the copy subprocess
  writes stdout to DEVNULL so a fork-holding child cannot hold the caller's
  capture pipes open, and stderr to a temp file — a pipe would reintroduce
  the hang — so a failing backend's diagnostic still reaches the user. The
  clipped harness now fakes the full Linux backend chain
  (xclip/xsel/wl-clipboard alongside pbcopy/pbpaste), so the suite is
  hermetic on machines that have real clipboard tools instead of reading and
  clobbering the developer's actual clipboard. The restart-stale harness
  passes Ansible's `systemctl --version` fact-gathering probe to the real
  systemctl unlogged, like its existing `ps` carve-out. The pii-redactor
  real-model tests skip with a named reason when the integration Ollama model
  is absent rather than failing as if the redactor were broken.
