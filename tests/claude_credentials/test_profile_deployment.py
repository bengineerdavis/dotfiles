"""Only safe settings deploy into the direct Claude profile."""

import subprocess

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT


def test_direct_profile_deploys_only_settings():
    result = subprocess.run(
        [
            "chezmoi",
            "-S",
            str(PAYLOAD_ROOT),
            "managed",
            "--path-style=source-relative",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    profile_files = [
        path
        for path in result.stdout.splitlines()
        if path.startswith("dot_claude-direct/")
    ]

    assert profile_files == ["dot_claude-direct/settings.json"]
