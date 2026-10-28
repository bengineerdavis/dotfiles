"""Match the topic's OpenCode fragment to `lore setup opencode`.

The setup command is the upstream contract. The topic cannot run it
directly: chezmoi owns opencode.jsonc, and when both files exist the
.jsonc wins, so setup's opencode.json would be shadowed. Instead the
fragment reproduces setup's output in the same (V1-compatible) config
shape, deep-merged ahead of the model overrides.

The parity test runs the real command in an isolated HOME with
--no-plugin (so no npm mutation and no gateway needed) and compares its
complete generated config with the fragment. A future Lore release that
changes setup output fails here rather than silently drifting.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess

import pytest

from loreai_service_helpers import TOPIC

LORE = shutil.which("lore") or os.path.expanduser("~/.local/bin/lore")
FRAGMENT = TOPIC / "files" / "opencode" / "lore-plugin.jsonc"


def run_setup(home) -> dict:
    """Run `lore setup opencode --no-plugin` in an isolated HOME."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("LORE_")}
    env["HOME"] = str(home)
    env["LORE_DB_PATH"] = str(home / "lore.db")
    env["LORE_CONFIG_DIR"] = str(home / "lore-config")
    env["LORE_NO_UPDATE_CHECK"] = "1"
    env["SENTRY_ENABLED"] = "0"
    result = subprocess.run(
        [LORE, "setup", "opencode", "--no-plugin"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    config = home / ".config" / "opencode" / "opencode.json"
    return json.loads(config.read_text())


@pytest.mark.skipif(not os.path.exists(LORE), reason="lore binary not installed")
def test_fragment_matches_lore_setup_opencode(tmp_path):
    generated = run_setup(tmp_path)
    fragment = json.loads(FRAGMENT.read_text())

    assert fragment == generated, (
        "The fragment must match the complete setup output. Review the new "
        "provider set deliberately: setup routes these providers, not local "
        "providers it does not declare (including Ollama). "
        f"Generated: {json.dumps(generated, sort_keys=True)}; "
        f"fragment: {json.dumps(fragment, sort_keys=True)}"
    )
