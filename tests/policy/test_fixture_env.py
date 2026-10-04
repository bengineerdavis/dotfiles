"""The fixtures' PATH construction: it must find a real uv, not a shim.

The mechanism these tests pin: a mise shim on the subprocess PATH re-enters
mise under the stripped HOME, fails its trust check against the real global
config, and exits 1 — which reads as DENIED, so deny-direction tests passed
while the resolver never answered. Whether a real uv binary is reachable
depends on how pytest was launched, so policy_harness.uv_dir scans every
PATH entry. These tests construct synthetic PATHs covering both orders and
the shim-only machine.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HARNESS = REPO / "tests" / "policy" / "policy_harness.py"
CONFTEST = REPO / "tests" / "policy" / "conftest.py"


@pytest.fixture
def harness():
    spec = importlib.util.spec_from_file_location("policy_harness_mod", HARNESS)
    # pyrefly: ignore [bad-argument-type]
    mod = importlib.util.module_from_spec(spec)
    # pyrefly: ignore [missing-attribute]
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def cf():
    spec = importlib.util.spec_from_file_location("policy_conftest", CONFTEST)
    # pyrefly: ignore [bad-argument-type]
    mod = importlib.util.module_from_spec(spec)
    # pyrefly: ignore [missing-attribute]
    spec.loader.exec_module(mod)
    return mod


def _make(tmp_path: pathlib.Path, shim: bool, real: bool) -> tuple[str, str]:
    """A shim dir and a real dir; the shim's target carries the exec bit."""
    shimdir = tmp_path / "shims"
    realdir = tmp_path / "installs" / "uv" / "latest" / "bin"
    if shim:
        shimdir.mkdir()
        (tmp_path / "mise").write_text("#!/bin/sh\n")
        (tmp_path / "mise").chmod(0o755)
        (shimdir / "uv").symlink_to(tmp_path / "mise")
    if real:
        realdir.mkdir(parents=True)
        (realdir / "uv").write_text("#!/bin/sh\n")
    return str(shimdir), str(realdir)


class TestUvDir:
    def test_prefers_real_uv_when_shim_comes_first(
        self, harness, tmp_path, monkeypatch
    ):
        shimdir, realdir = _make(tmp_path, shim=True, real=True)
        monkeypatch.setenv("PATH", f"{shimdir}:{realdir}")
        assert harness.uv_dir() == realdir

    def test_finds_real_uv_when_it_comes_first(self, harness, tmp_path, monkeypatch):
        shimdir, realdir = _make(tmp_path, shim=True, real=True)
        monkeypatch.setenv("PATH", f"{realdir}:{shimdir}")
        assert harness.uv_dir() == realdir

    def test_rejects_a_shim_resolving_to_mise(self, harness, tmp_path, monkeypatch):
        shimdir, _ = _make(tmp_path, shim=True, real=False)
        monkeypatch.setenv("PATH", shimdir)
        assert harness.uv_dir() == ""

    def test_returns_empty_without_any_uv(self, harness, tmp_path, monkeypatch):
        empty = tmp_path / "empty"
        empty.mkdir()
        monkeypatch.setenv("PATH", str(empty))
        assert harness.uv_dir() == ""


class TestPathWithUv:
    def test_puts_real_uv_first(self, cf, tmp_path, monkeypatch):
        shimdir, realdir = _make(tmp_path, shim=True, real=True)
        monkeypatch.setenv("PATH", f"{shimdir}:{realdir}")
        parts = cf._path_with_uv().split(":")
        assert parts[0] == realdir
        assert parts[1:] == ["/usr/bin", "/bin"]

    def test_falls_back_to_shim_dir_when_only_shim(self, cf, tmp_path, monkeypatch):
        shimdir, _ = _make(tmp_path, shim=True, real=False)
        monkeypatch.setenv("PATH", shimdir)
        parts = cf._path_with_uv().split(":")
        assert parts[0] == shimdir
        assert parts[1:] == ["/usr/bin", "/bin"]
