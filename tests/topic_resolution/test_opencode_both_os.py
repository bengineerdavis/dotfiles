"""opencode's `homebrew` dependency resolves on both OS families, for real.

This runs the role against the actual apps/*/topic.yml inventory — discovered
inside the play the same way the parent playbook discovers it — under both OS
families. `apps/opencode` requires `homebrew`; the two legs exercise the two
different legs of the `OK` state:

- Darwin: `homebrew` is provided by the in-run `apps/homebrew` topic, so it
  resolves via `provides_map_run`.
- Debian: `apps/homebrew` is Darwin-only, so it is not in the run. It resolves
  via the PATH probe for `brew` — this box runs linuxbrew, so `brew` is on PATH
  while no `homebrew` binary exists. Without the `homebrew -> brew` alias in
  `dependency_probe_binary` this leg fails.

`test_homebrew_probe_alias_is_brew` names that exact bug statically, so the
regression is caught even on a box where linuxbrew is absent and the Debian leg
could not fail for the right reason.

Run:
    pytest tests/topic_resolution/test_opencode_both_os.py -v
"""

from __future__ import annotations

import yaml
import pytest

# pyrefly: ignore [missing-import]
from topic_resolution_harness import DEFAULTS


@pytest.mark.parametrize("os_family", ["Darwin", "Debian"], ids=["darwin", "debian"])
def test_opencode_resolves(run_real, os_family):
    result = run_real(os_family)
    assert result.returncode == 0, (
        f"opencode should resolve on {os_family} against the real topic "
        f"metadata, but the run failed:\n{result.stdout}"
    )


def test_homebrew_probe_alias_is_brew():
    defaults = yaml.safe_load(DEFAULTS.read_text(encoding="utf-8"))
    probes = defaults["dependency_probe_binary"]
    assert probes.get("homebrew") == "brew", (
        "`homebrew` must probe the `brew` binary — no `homebrew` binary exists "
        "on any OS, so a missing (or identity) alias fails the Debian "
        "resolution leg (see roles/topic-resolution/defaults/main.yaml)"
    )
    # The dict legitimately grows as topics add probe aliases (bitwarden→bw,
    # 1password→op, 2026-09-20); each alias maps a topic_requires token to the
    # binary that actually exists — an alias whose value equals its own key is
    # the identity-probe bug this guard exists to catch.
    for token, binary in probes.items():
        assert binary != token, (
            f"probe alias {token!r} maps to itself — an identity alias "
            "defeats the probe (the token must name a binary that exists)"
        )
