"""Contract tests for the CALLERS of the policy resolver.

The rest of this suite proves the resolver answers correctly. Nothing proved that
anything ASKS it — and that gap has a specific, nasty shape:

    A guard that fails closed and a guard that never runs look identical.

Both refuse. Both look right in a smoke test. The difference only appears when
the policy says *yes*: a real guard changes behaviour, a broken one keeps
refusing forever.

This is not hypothetical. `ask-research` shipped for one commit with
`remote_permitted` defined AFTER the check that called it. bash reported "command
not found", returned 127, the guard refused, and every hand-test passed — while
the policy was never consulted at all. Relaxing the rule would have changed
nothing.

So every test here asserts BOTH directions. A test that only checks the denial is
worse than no test, because it certifies a guard that may not exist.

Run:
    pytest tests/policy/test_policy_callers.py -v
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import textwrap

import pytest

# pyrefly: ignore [missing-import]
from policy_harness import REPO, uv_dir

ASK_RESEARCH = REPO / "bin" / "executable_ask-research"

LOG_KEY = "boundaries.llm_processing.log_bodies_allowed"
REMOTE_KEY = "boundaries.llm_processing.remote_model_allowed"


def _company(**rules: bool) -> str:
    """A minimal company layer asserting only the rules a test cares about."""
    body = "\n".join(f"    {k}: {str(v).lower()}" for k, v in rules.items())
    return (
        textwrap.dedent(f"""
        meta:
          layer: company
          precedence: 2
        boundaries:
          llm_processing:
        """).lstrip("\n")
        + body
        + "\n"
    )


@pytest.fixture
def caller_env(tmp_path):
    """Run ask-research against a synthetic policy layer.

    NOTE the coupling this deliberately exercises: `policy` resolves the company
    layer from $XDG_STATE_HOME, and ask-research keeps its sessions there too.
    An earlier attempt at these tests set XDG_STATE_HOME only to isolate the
    session directory, which silently redirected the policy lookup to a path with
    no company layer — so the resolver returned unknown, the tool refused, and the
    test "passed" having proved nothing.
    """
    zsh = tmp_path / "dotfiles"
    state = tmp_path / "state"
    (zsh / "policy").mkdir(parents=True)
    (state / "ai-policy").mkdir(parents=True)
    brief = tmp_path / "brief.md"
    brief.write_text("a question\n")

    policy_src = REPO / "bin" / "executable_policy"
    shim = tmp_path / "shim"
    shim.mkdir()
    shutil.copy2(policy_src, shim / "policy")
    (shim / "policy").chmod(0o755)

    def build(company: str | None, *, on_path: bool = True):
        if company is not None:
            (state / "ai-policy" / "company.yaml").write_text(company)

        def run(*args: str) -> subprocess.CompletedProcess:
            base = os.environ.get("PATH", "")
            # uv_dir first: a mise shim on this PATH re-enters mise under the
            # stripped HOME and fails its trust check, so the resolver the
            # guard consults would answer ERROR-as-DENIED. See
            # policy_harness.uv_dir().
            uv = uv_dir()
            path = f"{uv}:{shim}:{base}" if on_path else f"{uv}:/usr/bin:/bin"
            return subprocess.run(
                [
                    "bash",
                    str(ASK_RESEARCH),
                    "start",
                    str(brief),
                    "--no-online",
                    "--dry-run",
                    *args,
                ],
                capture_output=True,
                text=True,
                env={
                    "ZSH": str(zsh),
                    "XDG_STATE_HOME": str(state),
                    "PATH": path,
                    "HOME": str(tmp_path),
                },
            )

        return run

    return build


def _sends(proc) -> bool:
    """Did it actually produce a command? Guards against vacuous assertions."""
    return any(ln.startswith("dry-run") for ln in proc.stderr.splitlines())


# --- remote inference: the guard must refuse, and must relent -----------------


def test_work_tagged_refuses_remote_when_denied(caller_env):
    run = caller_env(_company(remote_model_allowed=False))
    proc = run("--work-tagged")
    assert "cannot be sent to a remote model" in proc.stderr
    assert not _sends(proc), "refused but still produced a send command"


def test_work_tagged_proceeds_when_remote_is_permitted(caller_env):
    """The direction that distinguishes a guard from a corpse.

    If this fails while the test above passes, the guard is not consulting the
    resolver — it is refusing unconditionally.
    """
    run = caller_env(_company(remote_model_allowed=True, log_bodies_allowed=True))
    proc = run("--work-tagged")
    assert "cannot be sent to a remote model" not in proc.stderr
    assert _sends(proc), "permitted by policy but produced no command"


def test_untagged_is_unaffected_by_the_remote_rule(caller_env):
    """Without the tag there is no work content, so the boundary does not apply."""
    run = caller_env(_company(remote_model_allowed=False))
    proc = run()
    assert "cannot be sent to a remote model" not in proc.stderr
    assert _sends(proc)


def test_missing_resolver_still_refuses(caller_env):
    """Deleting the resolver must not turn remote inference back on."""
    run = caller_env(_company(remote_model_allowed=True), on_path=False)
    proc = run("--work-tagged")
    assert "cannot be sent to a remote model" in proc.stderr
    assert not _sends(proc)


# --- body logging: same pattern, degrade rather than refuse -------------------


def test_work_tagged_passes_no_log_when_logging_denied(caller_env):
    run = caller_env(_company(remote_model_allowed=True, log_bodies_allowed=False))
    proc = run("--work-tagged")
    assert _sends(proc), "should proceed; only logging is restricted"
    assert " -n " in proc.stderr, "logging denied but -n was not passed"


def test_work_tagged_omits_no_log_when_logging_permitted(caller_env):
    """The relenting direction again — proves the -n is policy-driven."""
    run = caller_env(_company(remote_model_allowed=True, log_bodies_allowed=True))
    proc = run("--work-tagged")
    assert _sends(proc)
    assert " -n " not in proc.stderr, "logging permitted but -n was passed anyway"


def test_untagged_never_passes_no_log(caller_env):
    run = caller_env(_company(log_bodies_allowed=False))
    proc = run()
    assert _sends(proc)
    assert " -n " not in proc.stderr
