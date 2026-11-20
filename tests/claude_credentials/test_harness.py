"""The credential harness finds the shell in its test environment."""

import pytest

from claude_credentials_harness import invoke


@pytest.mark.parametrize("environment", [{}, {"PATH": ""}, {"PATH": None}])
def test_invoke_fails_loudly_without_a_usable_path(environment):
    """The harness never falls back to the host shell.

    A missing PATH key, an empty value, and a None value all behave the
    same: no usable shell, so raise rather than search the host PATH.
    """
    with pytest.raises(RuntimeError, match="zsh is required"):
        invoke(environment, "unused")


def test_invoke_uses_zsh_from_the_supplied_path(tmp_path):
    """CI supplies /usr/bin/zsh; /bin/zsh is not required."""
    marker = tmp_path / "zsh-used"
    binary = tmp_path / "bin"
    binary.mkdir()
    zsh = binary / "zsh"
    zsh.write_text(f'#!/bin/sh\n: > "{marker}"\n')
    zsh.chmod(0o755)

    result = invoke({"PATH": str(binary)}, "unused")

    assert result.returncode == 0, result.stderr
    assert marker.exists()
