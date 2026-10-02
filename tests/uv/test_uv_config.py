"""The uv.toml template must resolve per machine: public PyPI only at home,
the private index as default on work machines, and a LOUD failure when a
work machine renders without the captured URL — a silent public-only render
on a work machine would be fail-open dependency confusion.

Renders run `chezmoi --source <fixture> execute-template --file <template>`
against a fixture source dir, so the host map is test-controlled and the
repo's template file is used unchanged. Verified empirically: execute-template
loads .chezmoidata from the active source dir (2026-10-01).
"""

from __future__ import annotations

import os
import pathlib
import shutil
import socket
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TEMPLATE = REPO / "dot_config" / "uv" / "uv.toml.tmpl"

pytestmark = pytest.mark.skipif(
    shutil.which("chezmoi") is None, reason="chezmoi not installed"
)


def _hosts_yaml(work: bool) -> str:
    return f"uv:\n  hosts:\n    {socket.gethostname()}:\n      work: {str(work).lower()}\n"


def render(tmp_path: pathlib.Path, hosts_yaml: str, *, env_url: str | None) -> subprocess.CompletedProcess:
    src = tmp_path / "source"
    (src / ".chezmoidata").mkdir(parents=True)
    (src / ".chezmoidata" / "uv.yaml").write_text(hosts_yaml, encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "UV_PRIVATE_INDEX_URL"}
    if env_url is not None:
        env["UV_PRIVATE_INDEX_URL"] = env_url
    return subprocess.run(
        ["chezmoi", "--source", str(src), "execute-template", "--file", str(TEMPLATE)],
        capture_output=True, text=True, env=env, cwd=str(tmp_path), timeout=60,
    )


def test_personal_renders_public_only(tmp_path):
    out = render(tmp_path, _hosts_yaml(work=False), env_url=None)
    assert out.returncode == 0, out.stderr
    assert "pypi.org/simple" in out.stdout
    assert "private" not in out.stdout
    assert 'required-version = ">=0.12.17"' in out.stdout


def test_work_host_renders_private_index_as_default(tmp_path):
    out = render(tmp_path, _hosts_yaml(work=True), env_url="https://pypi.example.internal/simple")
    assert out.returncode == 0, out.stderr
    assert 'name = "private"' in out.stdout
    assert 'url = "https://pypi.example.internal/simple"' in out.stdout
    assert out.stdout.index('name = "private"') < out.stdout.index('name = "public"')
    assert out.stdout.count("default = true") == 1
    # the private default sits before its public fallback
    assert out.stdout.index("default = true") < out.stdout.index('name = "public"')


def test_work_host_without_url_fails_loudly(tmp_path):
    out = render(tmp_path, _hosts_yaml(work=True), env_url=None)
    assert out.returncode != 0
    assert "UV_PRIVATE_INDEX_URL" in out.stderr, out.stderr


def test_url_without_work_flag_renders_public(tmp_path):
    """Fail-closed by design: the host flag decides, the env alone does not.
    A personal machine that happens to carry ~/.localrc must not silently
    route through a private index."""
    out = render(tmp_path, _hosts_yaml(work=False), env_url="https://pypi.example.internal/simple")
    assert out.returncode == 0, out.stderr
    assert "private" not in out.stdout
    assert "pypi.org/simple" in out.stdout


def test_unknown_host_renders_public(tmp_path):
    hosts = "uv:\n  hosts:\n    some-other-box:\n      work: true\n"
    out = render(tmp_path, hosts, env_url=None)
    assert out.returncode == 0, out.stderr
    assert "private" not in out.stdout
