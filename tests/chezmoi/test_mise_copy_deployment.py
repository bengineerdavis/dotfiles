"""The global mise config is deployed by apply, not by editing its source."""

from pathlib import Path
import shutil
import subprocess

import pytest

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

pytestmark = pytest.mark.skipif(
    shutil.which("chezmoi") is None, reason="chezmoi not installed"
)

SOURCE = PAYLOAD_ROOT / "dotfiles/apps/mise/files/config.toml"
TARGET = Path(".config/mise/config.toml")


def apply(source: Path, home: Path) -> None:
    """Apply only the global mise config into a disposable home."""
    (home / TARGET).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "chezmoi",
            "-S",
            str(source),
            "-D",
            str(home),
            "apply",
            "--force",
            str(home / TARGET),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_mise_config_is_a_regular_file_whose_source_edit_waits_for_apply(tmp_path):
    """A source edit must not silently deploy itself through a symlink."""
    source = tmp_path / "source"
    shutil.copytree(
        PAYLOAD_ROOT,
        source,
        ignore=shutil.ignore_patterns(".molecule", "__pycache__"),
    )
    source_config = source / SOURCE.relative_to(PAYLOAD_ROOT)
    original = source_config.read_text()
    home = tmp_path / "home"
    target = home / TARGET

    apply(source, home)

    assert target.is_file()
    assert not target.is_symlink()
    assert target.read_text() == original

    marker = "\n# source-only edit; must wait for chezmoi apply\n"
    source_config.write_text(original + marker)
    assert target.read_text() == original

    apply(source, home)
    assert target.read_text() == original + marker


def test_apply_replaces_a_preexisting_mise_symlink(tmp_path):
    """The one-time migration must not leave the old live symlink in place."""
    home = tmp_path / "home"
    target = home / TARGET
    target.parent.mkdir(parents=True)
    outside = tmp_path / "outside.toml"
    outside.write_text("pre-existing local content\n")
    target.symlink_to(outside)

    apply(PAYLOAD_ROOT, home)

    assert not target.is_symlink()
    assert target.read_text() == SOURCE.read_text()
    assert outside.read_text() == "pre-existing local content\n"


def test_mise_source_has_no_symlink_deployment_entries():
    """The conversion must not leave a second symlink source behind."""
    entries = list(PAYLOAD_ROOT.rglob("symlink_*"))
    assert entries == [], f"symlink deployment remains: {entries}"
