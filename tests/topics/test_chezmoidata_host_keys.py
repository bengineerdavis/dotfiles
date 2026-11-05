"""No committed file is keyed by a hardware serial.

Two surfaces commit hostname keys: `dotfiles/machines.yml` (see
`test_machines_registry_data.py`) and the `.chezmoidata` host maps. Both carried
the Mac's hardware serial until 2026-11-04.

The guard is deliberately narrow: it rejects the serial *shape* rather than
allowlisting names, so a new machine can be added without editing this test.
A hostname that fails `spec.md` § Data's string test must keep its values in an
unversioned machine-local file instead.
"""

from __future__ import annotations

import re

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import pytest
import yaml

SERIAL_SHAPE = re.compile(r"^[A-Z0-9]{10,}$")

# path -> how to reach that file's hostname-keyed map
HOST_MAPS = {
    ".chezmoidata/opencode.yaml": lambda data: (
        (data.get("opencode") or {}).get("hosts") or {}
    ),
    ".chezmoidata/uv.yaml": lambda data: (data.get("uv") or {}).get("hosts") or {},
}


@pytest.mark.parametrize("rel", sorted(HOST_MAPS))
def test_no_committed_host_key_is_serial_shaped(rel: str) -> None:
    path = PAYLOAD_ROOT / rel
    if not path.is_file():
        pytest.skip(f"{rel} not present")

    for key in HOST_MAPS[rel](yaml.safe_load(path.read_text())):
        assert not SERIAL_SHAPE.match(key), (
            f"{rel} is keyed by {key!r}, which looks like a hardware serial. "
            "A hostname that fails spec.md § Data's string test must not be "
            "committed; put its values in the machine-local overlay instead."
        )
