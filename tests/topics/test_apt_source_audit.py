"""apps/apt/files/apt_source_audit.py — report-only dead-source audit.

The fixture is real `apt-get update` output from 2026-09-22, the run that
exited 100 while proget.makedeb.org had been returning 530 for months.
"""

from __future__ import annotations

import importlib.util
import io
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "dotfiles" / "apps" / "apt" / "files" / "apt_source_audit.py"

APT_OUTPUT = """\
Get:1 https://cli.github.com/packages stable InRelease [3,917 B]
Hit:7 http://apt.pop-os.org/release jammy InRelease
Err:1 https://cli.github.com/packages stable InRelease
  The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 5612B36462313325
Err:21 https://proget.makedeb.org prebuilt-mpr InRelease
  530  <none> [IP: 104.21.67.130 443]
Reading package lists...
W: An error occurred during the signature verification. The repository is not updated and the previous index files will be used. GPG error: https://cli.github.com/packages stable InRelease: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 5612B36462313325
W: An error occurred during the signature verification. The repository is not updated and the previous index files will be used. GPG error: https://apt.releases.hashicorp.com jammy InRelease: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY FC9CA96ACA026560
E: Failed to fetch https://proget.makedeb.org/dists/prebuilt-mpr/InRelease  530  <none> [IP: 104.21.67.130 443]
E: The repository 'https://proget.makedeb.org prebuilt-mpr InRelease' is no longer signed.
N: Skipping acquire of configured file 'main/binary-i386/Packages' as repository 'http://deb.gierens.de stable InRelease' doesn't support architecture 'i386'
W: Skipping acquire of configured file 'main/binary-i386/Packages' as repository 'https://repos.azul.com/zulu/deb stable InRelease' doesn't support architecture 'i386'
"""


@pytest.fixture(scope="module")
def audit():
    spec = importlib.util.spec_from_file_location("apt_source_audit", SCRIPT)
    if spec is None:  # unreachable for a real path; narrows ModuleSpec | None
        raise RuntimeError("spec_from_file_location returned None")
    mod = importlib.util.module_from_spec(spec)
    if spec.loader is None:  # narrows Loader | None; set by spec_from_file_location
        raise RuntimeError("module spec carries no loader")
    spec.loader.exec_module(mod)
    return mod


def test_classifies_every_failing_host(audit):
    found = audit.parse(APT_OUTPUT)
    assert set(found) == {
        "cli.github.com",
        "apt.releases.hashicorp.com",
        "proget.makedeb.org",
    }
    assert found["cli.github.com"]["kinds"] == ["NO_PUBKEY 5612B36462313325"]
    assert found["apt.releases.hashicorp.com"]["kinds"] == [
        "NO_PUBKEY FC9CA96ACA026560"
    ]
    assert found["proget.makedeb.org"]["kinds"] == ["fetch-failed", "unsigned"]


def test_architecture_skips_are_not_failures(audit):
    found = audit.parse(APT_OUTPUT)
    assert "deb.gierens.de" not in found
    assert "repos.azul.com" not in found


def test_clean_update_reports_nothing(audit):
    assert (
        audit.parse(
            "Hit:1 http://apt.pop-os.org/release jammy InRelease\nReading package lists...\n"
        )
        == {}
    )


def test_counts_are_consecutive_and_reset_on_recovery(audit):
    failing = audit.parse(APT_OUTPUT)
    state, recovered = audit.update_state(
        {"proget.makedeb.org": 2, "old.example": 5}, failing
    )
    assert state["proget.makedeb.org"] == 3
    assert state["cli.github.com"] == 1
    assert "old.example" not in state
    assert recovered == ["old.example"]


def run_main(audit, monkeypatch, capsys, tmp_path, stdin, *extra):
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
    state = tmp_path / "state.json"
    assert audit.main(["--state", str(state), "--threshold", "3", *extra]) == 0
    return json.loads(capsys.readouterr().out), state


def test_host_is_flagged_only_at_threshold(audit, monkeypatch, capsys, tmp_path):
    for run, expected in ((1, False), (2, False), (3, True)):
        report, _ = run_main(audit, monkeypatch, capsys, tmp_path, APT_OUTPUT)
        proget = next(
            f for f in report["failures"] if f["host"] == "proget.makedeb.org"
        )
        assert proget["consecutive_runs"] == run
        assert proget["retirement_candidate"] is expected


def test_check_mode_writes_no_state(audit, monkeypatch, capsys, tmp_path):
    _, state = run_main(audit, monkeypatch, capsys, tmp_path, APT_OUTPUT, "--check")
    assert not state.exists()


def test_corrupt_state_file_starts_fresh(audit, monkeypatch, capsys, tmp_path):
    (tmp_path / "state.json").write_text("{not json")
    report, _ = run_main(audit, monkeypatch, capsys, tmp_path, APT_OUTPUT)
    assert all(f["consecutive_runs"] == 1 for f in report["failures"])
