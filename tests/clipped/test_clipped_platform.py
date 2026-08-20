"""
Platform dispatch for clipped.

This is the part the port was for. In bash the backend choice was three nested
layers of `case` and `command -v`, duplicated for copy and paste, and it could
only be exercised by mocking `uname` on PATH and running the whole script — so
in practice only the host's own platform was ever tested. Here the mapping and
the selection are functions, and every platform's preference order is checked on
any machine.
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import pathlib

import pytest

SCRIPT = pathlib.Path.home() / "bin" / "clipped"


@pytest.fixture(scope="module")
def clipped():
    if not SCRIPT.exists():
        pytest.skip(f"clipped not found at {SCRIPT}")
    loader = importlib.machinery.SourceFileLoader("clipped", str(SCRIPT))
    spec = importlib.util.spec_from_loader("clipped", loader, origin=str(SCRIPT))
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    loader.exec_module(mod)
    return mod


@pytest.mark.parametrize(
    ("system", "expected"),
    [
        ("Darwin", "Darwin"),
        ("Linux", "Linux"),
        ("FreeBSD", "Linux"),      # BSDs share the X11/Wayland tooling
        ("OpenBSD", "Linux"),
        ("NetBSD", "Linux"),
        ("CYGWIN_NT-10.0", "Windows"),
        ("MINGW64_NT-10.0", "Windows"),
        ("MSYS_NT-10.0", "Windows"),
        ("Windows", "Windows"),
        # Anything unrecognised falls in with Linux, whose candidate list ends
        # in pbcopy/pbpaste — an unknown Unix still gets a chance to work.
        ("Plan9", "Linux"),
        ("", "Linux"),
    ],
)
def test_platform_key_mapping(clipped, system, expected):
    assert clipped.platform_key(system) == expected


def test_darwin_prefers_pbcopy(clipped, monkeypatch):
    monkeypatch.setattr(clipped.shutil, "which", lambda name: f"/usr/bin/{name}")
    assert clipped.find_backend("copy", "Darwin") == ["pbcopy"]
    assert clipped.find_backend("paste", "Darwin") == ["pbpaste"]


def test_linux_prefers_xclip_when_everything_is_present(clipped, monkeypatch):
    monkeypatch.setattr(clipped.shutil, "which", lambda name: f"/usr/bin/{name}")
    assert clipped.find_backend("copy", "Linux")[0] == "xclip"
    assert clipped.find_backend("paste", "Linux")[0] == "xclip"


@pytest.mark.parametrize(
    ("available", "expected_copy", "expected_paste"),
    [
        ({"xclip"},   "xclip",   "xclip"),
        ({"xsel"},    "xsel",    "xsel"),
        ({"wl-copy", "wl-paste"}, "wl-copy", "wl-paste"),
        # Homebrew-on-Linux case: only the macOS tools are present.
        ({"pbcopy", "pbpaste"},   "pbcopy", "pbpaste"),
        # Preference order holds when several are installed at once.
        ({"xsel", "wl-copy", "wl-paste", "pbcopy", "pbpaste"}, "xsel", "xsel"),
    ],
)
def test_linux_falls_through_preference_order(
    clipped, monkeypatch, available, expected_copy, expected_paste
):
    monkeypatch.setattr(
        clipped.shutil, "which", lambda name: f"/usr/bin/{name}" if name in available else None
    )
    assert clipped.find_backend("copy", "Linux")[0] == expected_copy
    assert clipped.find_backend("paste", "Linux")[0] == expected_paste


def test_windows_uses_clip_and_powershell(clipped, monkeypatch):
    monkeypatch.setattr(clipped.shutil, "which", lambda name: f"/c/{name}")
    assert clipped.find_backend("copy", "Windows")[0] == "clip.exe"
    assert clipped.find_backend("paste", "Windows")[0] == "powershell.exe"


def test_no_backend_exits_with_install_guidance(clipped, monkeypatch, capsys):
    monkeypatch.setattr(clipped.shutil, "which", lambda name: None)
    with pytest.raises(SystemExit) as exc:
        clipped.find_backend("copy", "Linux")
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "no clipboard utility found" in err
    # The message must name what to install, not just report failure.
    assert "xclip" in err and "apt install" in err
