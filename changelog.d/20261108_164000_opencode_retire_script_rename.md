### Fixed

- The opencode legacy-config retire helper was named
  `run_before_before_retire-opencode-json.py`, which chezmoi parsed as a
  `run_before_` hook onto a nonexistent target
  `.config/opencode/before_retire-opencode-json.py`, leaving a permanent `R`
  (remove) entry in `chezmoi status`. Renamed to
  `run_before_retire-opencode-json.py` to match the target the script actually
  guards (`retire-opencode-json.py`, script-only, never deployed). The helper's
  behaviour is unchanged.