"""Retire a shadowed opencode.json through chezmoi's deployment seam.

Chezmoi owns the global OpenCode config. The run_before_ script under
dot_config/opencode backs up the legacy .json verbatim before removing it,
so the winning .jsonc is the only active global config and no helper is
installed as application state. Direct tests exercise the helper's failure
paths; the integration test drives a real chezmoi apply in an isolated home.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

SCRIPT = (
    PAYLOAD_ROOT
    / "dot_config"
    / "opencode"
    / "run_before_before_retire-opencode-json.py"
)
CHEZMOI = shutil.which("chezmoi")

_spec = spec_from_file_location("retire_opencode_json", SCRIPT)
assert _spec and _spec.loader
retire_module = module_from_spec(_spec)
_spec.loader.exec_module(retire_module)
retire_legacy_config = retire_module.retire_legacy_config


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    config = tmp_path / "home" / ".config" / "opencode"
    config.mkdir(parents=True)
    (config / "opencode.jsonc").write_text(
        '// managed\n{"plugin":[],"model":"openrouter/winning"}\n'
    )
    return config


def test_absent_legacy_config_is_a_noop(config_dir: Path):
    assert retire_legacy_config(config_dir) is False
    assert not (config_dir / "opencode.json.pre-jsonc-backup").exists()


@pytest.mark.parametrize(
    "model",
    ["openrouter/winning", "openrouter/local-override"],
    ids=["equivalent", "different"],
)
def test_legacy_config_is_backed_up_verbatim_and_removed(config_dir: Path, model: str):
    # Differing values were never active: jsonc wins. Preserve them verbatim
    # rather than blocking convergence or silently discarding the file.
    payload = json.dumps({"plugin": [], "model": model}).encode() + b"\n"
    (config_dir / "opencode.json").write_bytes(payload)

    assert retire_legacy_config(config_dir) is True
    assert not (config_dir / "opencode.json").exists()
    assert (config_dir / "opencode.json.pre-jsonc-backup").read_bytes() == payload

    # A second run sees no legacy file and must not touch the backup.
    assert retire_legacy_config(config_dir) is False
    assert (config_dir / "opencode.json.pre-jsonc-backup").read_bytes() == payload


def test_missing_jsonc_stops_cleanup_without_creating_a_backup(config_dir: Path):
    (config_dir / "opencode.jsonc").unlink()
    (config_dir / "opencode.json").write_text('{"plugin":[]}\n')

    with pytest.raises(RuntimeError, match="Nothing was moved or deleted"):
        retire_legacy_config(config_dir)
    assert (config_dir / "opencode.json").exists()
    assert not (config_dir / "opencode.json.pre-jsonc-backup").exists()


def test_existing_backup_stops_cleanup_without_touching_either_file(config_dir: Path):
    (config_dir / "opencode.json").write_text('{"plugin":[]}\n')
    backup = config_dir / "opencode.json.pre-jsonc-backup"
    backup.write_text('{"preserved":true}\n')

    with pytest.raises(RuntimeError, match="already exists"):
        retire_legacy_config(config_dir)
    assert (config_dir / "opencode.json").exists()
    assert json.loads(backup.read_text()) == {"preserved": True}


def test_readback_mismatch_preserves_original_and_publishes_no_backup(
    config_dir: Path, monkeypatch: pytest.MonkeyPatch
):
    (config_dir / "opencode.json").write_text('{"plugin":[]}\n')
    real_read_bytes = Path.read_bytes

    def corrupt_temporary(self: Path) -> bytes:
        data = real_read_bytes(self)
        if self.name.startswith(".opencode.json.pre-jsonc-backup."):
            return b"corrupted"
        return data

    monkeypatch.setattr(Path, "read_bytes", corrupt_temporary)

    with pytest.raises(RuntimeError, match="Backup verification failed"):
        retire_legacy_config(config_dir)
    assert (config_dir / "opencode.json").exists()
    assert not (config_dir / "opencode.json.pre-jsonc-backup").exists()
    assert not list(config_dir.glob(".opencode.json.pre-jsonc-backup.*"))


def test_published_backup_mismatch_preserves_original(
    config_dir: Path, monkeypatch: pytest.MonkeyPatch
):
    (config_dir / "opencode.json").write_text('{"plugin":[]}\n')
    real_read_bytes = Path.read_bytes

    def corrupt_published_backup(self: Path) -> bytes:
        if self.name == "opencode.json.pre-jsonc-backup":
            return b"corrupted"
        return real_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", corrupt_published_backup)

    with pytest.raises(RuntimeError, match="Published backup verification failed"):
        retire_legacy_config(config_dir)
    assert (config_dir / "opencode.json").exists()


def test_backup_race_preserves_original_and_never_overwrites(
    config_dir: Path, monkeypatch: pytest.MonkeyPatch
):
    (config_dir / "opencode.json").write_text('{"plugin":[]}\n')
    real_link = os.link

    def racing_link(src, dst, **kwargs):
        # Another process wins the backup path between the existence check
        # and publication. Its contents must survive.
        Path(dst).write_text('{"other-writer":true}\n')
        return real_link(src, dst, **kwargs)

    monkeypatch.setattr(retire_module.os, "link", racing_link)

    with pytest.raises(OSError):
        retire_legacy_config(config_dir)
    assert (config_dir / "opencode.json").exists()
    assert json.loads((config_dir / "opencode.json.pre-jsonc-backup").read_text()) == {
        "other-writer": True
    }


@pytest.mark.skipif(CHEZMOI is None, reason="chezmoi not on PATH")
def test_chezmoi_apply_runs_migration_and_deploys_no_script_artifact(tmp_path: Path):
    if CHEZMOI is None:
        raise RuntimeError("chezmoi is required for this fixture")
    home = tmp_path / "isolated-home"
    config = home / ".config" / "opencode"
    config.mkdir(parents=True)
    payload = b'{"plugin":[],"model":"openrouter/shadowed"}\n'
    (config / "opencode.json").write_bytes(payload)
    (config / "opencode.jsonc").write_text('{"plugin":[]}\n')
    chezmoi_config = tmp_path / "chezmoi.yaml"
    chezmoi_config.write_text('pager: ""\n')

    def apply() -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                CHEZMOI,
                "-S",
                str(PAYLOAD_ROOT),
                "-D",
                str(home),
                "-c",
                str(chezmoi_config),
                "--no-tty",
                "--no-pager",
                "apply",
                "--include=scripts",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    result = apply()
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (config / "opencode.json").exists()
    assert (config / "opencode.json.pre-jsonc-backup").read_bytes() == payload
    # run_before_ executes the script; it must not deploy a Python artifact.
    assert not (config / "retire-opencode-json.py").exists()

    second = apply()
    assert second.returncode == 0, second.stdout + second.stderr
    assert (config / "opencode.json.pre-jsonc-backup").read_bytes() == payload
