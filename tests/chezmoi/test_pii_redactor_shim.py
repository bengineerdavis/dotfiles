"""The pii-redactor shim is repo-owned behaviour, so it needs its own tests.

The 1180-line suite moved to the pii-redaction skill with the implementation, and
it grades the redactor — not this wrapper. Everything the wrapper promises is
about *which* implementation it reaches and *what it says* when it reaches none:

  - an explicit PII_REDACTOR_SKILL_SCRIPT wins over the discovered candidates;
  - a bad override produces its own message, distinct from "skill not installed",
    because the two need different fixes;
  - no candidate at all names what is missing and how to install it;
  - a working candidate is exec'd with arguments forwarded untouched.

None of that is pinned by the moved suite. A future edit that reorders the
candidates, collapses the two error messages, or drops the status propagation
would leave every existing test green while the wrapper lied to the operator.

The tests run the real script under bash with HOME pointed at a sandbox, so
discovery cannot escape into the machine's actual ~/.agents or ~/code.
"""

from __future__ import annotations

import os
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SHIM = REPO / "home" / "bin" / "executable_pii-redactor"


def run_shim(
    args: list[str] | None = None,
    *,
    home: pathlib.Path,
    override: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run the shim with a sandboxed HOME and no inherited override."""
    env = {k: v for k, v in os.environ.items() if k != "PII_REDACTOR_SKILL_SCRIPT"}
    env["HOME"] = str(home)
    if override is not None:
        env["PII_REDACTOR_SKILL_SCRIPT"] = override
    return subprocess.run(
        ["bash", str(SHIM), *(args or [])],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def install_fake_skill(home: pathlib.Path, body: str) -> pathlib.Path:
    """Write a stand-in implementation where discovery looks for it."""
    script = home / ".agents" / "skills" / "pii-redaction" / "scripts" / "pii-redactor"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(body, encoding="utf-8")
    script.chmod(0o755)
    return script


@pytest.fixture()
def sandbox(tmp_path: pathlib.Path) -> pathlib.Path:
    home = tmp_path / "home"
    home.mkdir()
    return home


def test_the_shim_exists_and_is_a_bash_script() -> None:
    """A missing or non-bash shim makes every other test here meaningless."""
    assert SHIM.is_file(), f"{SHIM} is missing"
    first = SHIM.read_text(encoding="utf-8").splitlines()[0]
    assert first.startswith("#!") and "bash" in first, first


def test_an_override_wins_over_a_discovered_candidate(sandbox: pathlib.Path) -> None:
    """The override exists so an operator can grade a checkout deliberately."""
    install_fake_skill(sandbox, "#!/usr/bin/env bash\necho discovered\n")
    chosen = sandbox / "chosen"
    chosen.write_text("#!/usr/bin/env bash\necho override\n", encoding="utf-8")
    chosen.chmod(0o755)

    result = run_shim(home=sandbox, override=str(chosen))

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "override"


def test_a_bad_override_names_the_override_not_the_missing_skill(
    sandbox: pathlib.Path,
) -> None:
    """Two failure modes, two messages: they need different fixes.

    This is the finding that prompted the test. A typo'd override used to reach
    `exec` and surface as a bare "No such file or directory", which says nothing
    about which of the three paths was wrong.
    """
    install_fake_skill(sandbox, "#!/usr/bin/env bash\necho discovered\n")
    missing = str(sandbox / "no-such-file")

    result = run_shim(home=sandbox, override=missing)

    assert result.returncode == 1
    assert "PII_REDACTOR_SKILL_SCRIPT" in result.stderr
    assert missing in result.stderr
    # The "not installed" message would send the operator to install the skill,
    # which is the wrong fix for a typo.
    assert "was not found" not in result.stderr


def test_no_candidate_names_what_is_missing_and_how_to_install(
    sandbox: pathlib.Path,
) -> None:
    """A wrapper that silently does nothing is worse than one that fails loudly."""
    result = run_shim(home=sandbox)

    assert result.returncode == 1
    assert "was not found" in result.stderr
    assert (
        "ai-prompt-library/skills/pii-redaction/scripts/pii-redactor" in result.stderr
    )
    assert "dotagents" in result.stderr


def test_arguments_reach_the_implementation_untouched(
    sandbox: pathlib.Path,
) -> None:
    """`exec "$target" "$@"` is the whole point of a shim.

    The values are chosen to include a flag-like argument and one containing a
    space, since a wrapper that re-quoted or re-split would corrupt both.
    """
    install_fake_skill(
        sandbox,
        '#!/usr/bin/env bash\nprintf "<%s>\\n" "$@"\n',
    )

    result = run_shim(["--input", "a file.md", "-o", "out.md"], home=sandbox)

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "<--input>",
        "<a file.md>",
        "<-o>",
        "<out.md>",
    ]


def test_the_implementations_exit_status_is_the_shims(
    sandbox: pathlib.Path,
) -> None:
    """`exec` preserves status; a wrapper that captured and re-ran would not.

    Redaction exits non-zero on an unproven run, so the shim must not turn a
    failed redaction into a success at the shell boundary.
    """
    install_fake_skill(sandbox, "#!/usr/bin/env bash\nexit 3\n")

    result = run_shim(home=sandbox)

    assert result.returncode == 3
