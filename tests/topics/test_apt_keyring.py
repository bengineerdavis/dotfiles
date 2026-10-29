"""apps/apt/files/apt_keyring.py — the keyring repair that must not write garbage.

The helper replaced a get_url task that saved an HTML page and an empty file as
keyrings and reported success. These tests pin the property that matters: a
download that is not an OpenPGP public key never reaches the destination, and
the destination is read from the source file rather than guessed.

Real gpg, throwaway GNUPGHOME, no network: `fetch` is injected.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import pathlib
import shutil
import subprocess
import tempfile

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import pytest

SCRIPT = PAYLOAD_ROOT / "dotfiles" / "apps" / "apt" / "files" / "apt_keyring.py"

pytestmark = pytest.mark.skipif(shutil.which("gpg") is None, reason="needs gpg")

# Unix-domain sockets bind no longer than 104 bytes (macOS sun_path). gpg-agent
# listens on <GNUPGHOME>/S.gpg-agent, so a long homedir silently kills the agent
# ("agent_genkey failed: No agent running"). pytest's tmp_path_factory resolves
# to the long /private/var/... realpath and its per-run counter only grows, so
# homedirs under it cross the limit and the fixture fails intermittently by
# nothing but path length. The fixture therefore takes a SHORT mkdtemp home.
SOCKET_LIMIT = 104


@pytest.fixture(scope="module")
def ak():
    spec = importlib.util.spec_from_file_location("apt_keyring", SCRIPT)
    if spec is None:  # unreachable for a real path; narrows ModuleSpec | None
        raise RuntimeError("spec_from_file_location returned None")
    mod = importlib.util.module_from_spec(spec)
    if spec.loader is None:  # narrows Loader | None; set by spec_from_file_location
        raise RuntimeError("module spec carries no loader")
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gnupg_home():
    """A short-lived GNUPGHOME short enough for gpg-agent's socket."""
    home = pathlib.Path(tempfile.mkdtemp(prefix="aptkr-gpg-"))
    os.chmod(home, 0o700)
    yield home
    shutil.rmtree(home, ignore_errors=True)


@pytest.fixture(scope="module")
def pubkey(gnupg_home):
    """(armored, binary, key_id) for a freshly generated throwaway key."""
    env = {**os.environ, "GNUPGHOME": str(gnupg_home)}
    subprocess.run(
        [
            "gpg",
            "--batch",
            "--pinentry-mode",
            "loopback",
            "--passphrase",
            "",
            "--quick-gen-key",
            "Test Repo <test@example.invalid>",
            "ed25519",
            "sign",
            "never",
        ],
        env=env,
        check=True,
        capture_output=True,
    )
    armored = subprocess.run(
        ["gpg", "--armor", "--export"], env=env, check=True, capture_output=True
    ).stdout
    binary = subprocess.run(
        ["gpg", "--export"], env=env, check=True, capture_output=True
    ).stdout
    listing = subprocess.run(
        ["gpg", "--with-colons", "--list-keys"],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    key_id = next(
        line.split(":")[4] for line in listing.splitlines() if line.startswith("pub:")
    )
    return armored, binary, key_id


def args(tmp_path, **over):
    base = {
        "name": "test",
        "repo_host": "repo.example.invalid",
        "url": "https://repo.example.invalid/key",
        "require_key": [],
        "sources_dir": str(tmp_path / "sources.list.d"),
        "sources_list": str(tmp_path / "sources.list"),
        "timeout": 5,
        "check": False,
    }
    base.update(over)
    return argparse.Namespace(**base)


def list_source(tmp_path, dest, name="repo.list"):
    d = tmp_path / "sources.list.d"
    d.mkdir(exist_ok=True)
    (d / name).write_text(
        f"deb [arch=amd64 signed-by={dest}] https://repo.example.invalid stable main\n"
    )


# ── destination discovery ─────────────────────────────────────────────────────


def test_dest_comes_from_signed_by_not_a_default(ak, tmp_path, pubkey):
    armored, _, _ = pubkey
    dest = tmp_path / "usr-share-keyrings" / "repo.gpg"
    list_source(tmp_path, dest)
    report = ak.repair(args(tmp_path), fetch=lambda u, t: armored)
    assert report["dest"] == str(dest)
    assert dest.is_file()


def test_deb822_signed_by_is_read(ak, tmp_path):
    d = tmp_path / "sources.list.d"
    d.mkdir()
    (d / "repo.sources").write_text(
        "Types: deb\nURIs: https://repo.example.invalid\nSuites: stable\n"
        "Components: main\nSigned-By: /usr/share/keyrings/custom.gpg\n"
    )
    _, dest = ak.find_keyring_dest(
        "repo.example.invalid", ak.candidate_sources(d, tmp_path / "none")
    )
    assert dest == "/usr/share/keyrings/custom.gpg"


def test_commented_out_source_is_not_repaired(ak, tmp_path, pubkey):
    d = tmp_path / "sources.list.d"
    d.mkdir()
    (d / "repo.list").write_text(
        "# deb [signed-by=/x.gpg] https://repo.example.invalid stable main\n"
    )
    report = ak.repair(
        args(tmp_path), fetch=lambda u, t: pytest.fail("must not download")
    )
    assert report["status"] == "no-source"


def test_disabled_deb822_source_is_not_repaired(ak, tmp_path):
    d = tmp_path / "sources.list.d"
    d.mkdir()
    (d / "repo.sources").write_text(
        "Enabled: no\nTypes: deb\n"
        "URIs: https://repo.example.invalid\nSigned-By: /x.gpg\n"
    )
    report = ak.repair(
        args(tmp_path), fetch=lambda u, t: pytest.fail("must not download")
    )
    assert report["status"] == "no-source"


def test_source_without_signed_by_fails_loudly(ak, tmp_path):
    d = tmp_path / "sources.list.d"
    d.mkdir()
    (d / "repo.list").write_text("deb https://repo.example.invalid stable main\n")
    with pytest.raises(ak.RepairError, match="names no keyring file"):
        ak.repair(args(tmp_path), fetch=lambda u, t: b"")


# ── the property the old task lacked: garbage never lands ─────────────────────


@pytest.mark.parametrize(
    "payload",
    [
        b"",
        b"<!DOCTYPE html><html><body>Not Found</body></html>" * 500,
        b"-----BEGIN PGP PUBLIC KEY BLOCK-----\n\ngarbage\n"
        b"-----END PGP PUBLIC KEY BLOCK-----\n",
    ],
)
def test_non_key_download_is_refused_and_dest_untouched(ak, tmp_path, payload):
    dest = tmp_path / "repo.gpg"
    dest.write_bytes(b"previous")
    list_source(tmp_path, dest)
    with pytest.raises(ak.RepairError):
        ak.repair(args(tmp_path), fetch=lambda u, t: payload)
    assert dest.read_bytes() == b"previous"


def test_armored_key_is_dearmored_before_writing(ak, tmp_path, pubkey):
    armored, _, key_id = pubkey
    dest = tmp_path / "repo.gpg"
    list_source(tmp_path, dest)
    report = ak.repair(args(tmp_path), fetch=lambda u, t: armored)
    assert report["status"] == "repaired"
    assert not dest.read_bytes().startswith(b"-----BEGIN")
    assert ak.key_ids(dest.read_bytes()) == [key_id]
    assert oct(dest.stat().st_mode & 0o777) == "0o644"


def test_required_key_missing_is_refused(ak, tmp_path, pubkey):
    armored, _, _ = pubkey
    dest = tmp_path / "repo.gpg"
    list_source(tmp_path, dest)
    with pytest.raises(ak.RepairError, match="not the required"):
        ak.repair(
            args(tmp_path, require_key=["5612B36462313325"]), fetch=lambda u, t: armored
        )
    assert not dest.exists()


def test_required_key_present_passes_case_insensitively(ak, tmp_path, pubkey):
    armored, _, key_id = pubkey
    dest = tmp_path / "repo.gpg"
    list_source(tmp_path, dest)
    report = ak.repair(
        args(tmp_path, require_key=[key_id.lower()]), fetch=lambda u, t: armored
    )
    assert report["keys"] == [key_id]


# ── idempotency and check mode ────────────────────────────────────────────────


def test_second_run_is_unchanged(ak, tmp_path, pubkey):
    armored, _, _ = pubkey
    dest = tmp_path / "repo.gpg"
    list_source(tmp_path, dest)
    first = ak.repair(args(tmp_path), fetch=lambda u, t: armored)
    second = ak.repair(args(tmp_path), fetch=lambda u, t: armored)
    assert first["changed"] is True
    assert second["changed"] is False and second["status"] == "ok"


def test_check_mode_reports_without_writing(ak, tmp_path, pubkey):
    armored, _, _ = pubkey
    dest = tmp_path / "repo.gpg"
    dest.write_bytes(b"")
    list_source(tmp_path, dest)
    report = ak.repair(args(tmp_path, check=True), fetch=lambda u, t: armored)
    assert report["status"] == "would-repair" and report["before"] == "empty"
    assert dest.read_bytes() == b""


def test_main_exit_code_and_json(ak, tmp_path, capsys):
    rc = ak.main(
        [
            "--name",
            "t",
            "--repo-host",
            "repo.example.invalid",
            "--url",
            "https://x.invalid/k",
            "--sources-dir",
            str(tmp_path / "none"),
            "--sources-list",
            str(tmp_path / "none2"),
        ]
    )
    assert rc == 0
    assert '"status": "no-source"' in capsys.readouterr().out


def test_gnupghome_fits_the_unix_socket_limit(gnupg_home):
    """The homedir handed to gpg must keep S.gpg-agent under the sun_path cap.

    Bound on 2026-10-20 after the fixture began failing intermittently: gpg
    reports "agent_genkey failed: No agent running" when the agent socket
    path exceeds the kernel's 104-byte limit — and pytest's tmp_path_factory
    resolves to the long /private/var/... realpath whose per-run counter only
    grows, so the old fixture crossed the line by nothing but path length.
    """
    socket = gnupg_home / "S.gpg-agent"
    assert len(str(socket)) <= SOCKET_LIMIT, (
        f"{socket} is {len(str(socket))} chars; gpg-agent's unix socket "
        f"binds at most {SOCKET_LIMIT}"
    )
