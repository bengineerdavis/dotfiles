import pathlib
import subprocess

import pytest

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

SCRIPT = PAYLOAD_ROOT / "dotfiles" / "executable_run-role.sh"


@pytest.fixture
def run_script(tmp_path):
    """Run the real run-role.sh from a foreign cwd, fake mise on PATH.

    The fake mise records its argv and exits 0, so the script's
    playbook check and argument wiring are exercised without
    ansible, a topic run, or the network.
    """
    fake_bin = tmp_path / "fakebin"
    fake_bin.mkdir()
    log = tmp_path / "mise-args.log"
    fake_mise = fake_bin / "mise"
    fake_mise.write_text('#!/bin/sh\necho "$@" >> "$FAKE_MISE_LOG"\n')
    fake_mise.chmod(0o755)

    env = {
        "PATH": f"{fake_bin}:/usr/bin:/bin",
        "FAKE_MISE_LOG": str(log),
        "HOME": str(tmp_path),
    }

    def run(cwd, *args):
        return subprocess.run(
            ["bash", str(SCRIPT), *args],
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

    return run, log
