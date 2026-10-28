"""Shared environment behavior for the Lore gateway service."""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest
import yaml

from loreai_service_helpers import JINJA, TOPIC, render_env_file


@pytest.mark.parametrize("shell", ["bash", "dash"])
def test_env_file_resolves_openrouter_key_in_service_shells(tmp_path, shell):
    """One env file works in launchd and Debian service shells."""
    shell_path = shutil.which(shell)
    if shell_path is None:
        pytest.skip(f"{shell} is not installed on this host")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    llm = bin_dir / "llm"
    llm.write_text("#!/bin/sh\nprintf 'dummy-openrouter-key\\n'\n")
    llm.chmod(0o755)
    env_file = tmp_path / "env.zsh"
    env_file.write_text(render_env_file())

    result = subprocess.run(
        [
            shell_path,
            "-c",
            '. "$1" && [ "$OPENROUTER_API_KEY" = "dummy-openrouter-key" ] '
            '&& [ "$LORE_WORKER_API_KEY" = "dummy-openrouter-key" ]',
            "lore-env-test",
            str(env_file),
        ],
        env={
            "HOME": str(tmp_path),
            "PATH": f"{bin_dir}:{os.defpath}",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_env_file_routes_openai_protocol_to_openrouter():
    expected = 'export LORE_UPSTREAM_OPENAI="https://openrouter.ai/api"'
    assert expected in render_env_file()


def test_service_path_uses_stable_mise_shims():
    defaults = yaml.safe_load((TOPIC / "defaults" / "main.yaml").read_text())
    rendered = JINJA.from_string(defaults["loreai_service_path"]).render(
        ansible_env={"HOME": "/home/test"}
    )
    assert rendered == (
        "/home/test/.local/bin:/home/test/.local/share/mise/shims:"
        "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    )
