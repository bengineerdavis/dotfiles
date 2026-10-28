"""A throwaway OpenCode session records in an isolated Lore database.

Opt-in (`llm_judge`): needs the real binaries and OPENROUTER_API_KEY.
Excluded from the default suite. It never uses the live Lore gateway or
database.
"""

from __future__ import annotations

from collections.abc import Iterator
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import time

import pytest

LORE = shutil.which("lore") or os.path.expanduser("~/.local/bin/lore")
MODEL = "openrouter/z-ai/glm-5.3-flash"

pytestmark = [
    pytest.mark.llm_judge,
    pytest.mark.skipif(shutil.which("opencode") is None, reason="opencode missing"),
    pytest.mark.skipif(not os.path.exists(LORE), reason="lore binary missing"),
    pytest.mark.skipif(
        not os.environ.get("OPENROUTER_API_KEY"), reason="OPENROUTER_API_KEY unset"
    ),
]


def run(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        command, capture_output=True, text=True, check=False, **kwargs
    )


def isolated_environment(project: Path) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("OPENCODE", "LORE_"))
    }
    # OpenCode also consults PWD. A subprocess cwd does not update it,
    # so an inherited value selects the caller's repository.
    env["PWD"] = str(project)
    for name in ("CONFIG", "DATA", "CACHE", "STATE"):
        path = project / f".{name.lower()}"
        path.mkdir()
        env[f"XDG_{name}_HOME"] = str(path)
    env["LORE_DB_PATH"] = str(project / "lore.db")
    env["LORE_CONFIG_DIR"] = str(project / ".lore-config")
    # Match the documented machine worker/provider routing explicitly.
    env["LORE_UPSTREAM_OPENAI"] = "https://openrouter.ai/api"
    env["LORE_NO_UPDATE_CHECK"] = "1"
    env["SENTRY_ENABLED"] = "0"
    return env


def wait_for_gateway(process: subprocess.Popen, port: int, log) -> None:
    for _ in range(60):
        if process.poll() is not None:
            log.flush()
            raise AssertionError(
                f"isolated gateway exited with {process.returncode}: "
                f"{Path(log.name).read_text()[-2000:]}"
            )
        ready = run(
            ["curl", "-sf", "-o", "/dev/null", f"http://127.0.0.1:{port}/health"],
            timeout=2,
        )
        if ready.returncode == 0:
            return
        time.sleep(0.5)
    raise AssertionError(f"isolated gateway did not start on port {port}")


def stop_gateway(process: subprocess.Popen) -> None:
    # The group can outlive its leader, so clean up even if it exited.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=10)
    assert process.poll() is not None, "isolated gateway is still running"


@pytest.fixture
def isolated_gateway(tmp_path: Path) -> Iterator[tuple[Path, int, dict[str, str]]]:
    project = tmp_path / "project"
    project.mkdir()
    env = isolated_environment(project)
    # Configure the gateway before startup: no background curation or
    # writes to project-owned memory/instruction files.
    (project / ".lore.json").write_text(
        json.dumps(
            {
                "curator": {"enabled": False},
                "loreFile": {"enabled": False},
                "agentsFile": {"enabled": False},
            }
        )
    )
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    log_path = tmp_path / "gateway.log"
    with log_path.open("w") as log:
        process = subprocess.Popen(
            [LORE, "start", "--local", "--port", str(port)],
            cwd=project,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            wait_for_gateway(process, port, log)
            yield project, port, env
        finally:
            stop_gateway(process)


def live_project_paths() -> set[str]:
    result = run([LORE, "data", "list", "projects", "--json"], timeout=30)
    assert result.returncode == 0, result.stderr
    return {entry["path"] for entry in json.loads(result.stdout or "[]")}


def run_throwaway_session(project: Path, port: int, env: dict[str, str]):
    (project / "opencode.jsonc").write_text(
        json.dumps(
            {
                "provider": {
                    "openrouter": {
                        "options": {
                            "baseURL": f"http://127.0.0.1:{port}/v1",
                            "headers": {
                                "X-Lore-Project": str(project),
                                "X-Lore-Agent": "coder",
                            },
                        }
                    }
                },
                "model": MODEL,
                # Keep background title requests on this isolated route.
                "agents": {"title": {"model": MODEL}},
            }
        )
    )
    return run(
        [
            "opencode",
            "run",
            "--standalone",
            "--format",
            "json",
            "--model",
            MODEL,
            "Reply with exactly OK.",
        ],
        cwd=project,
        env=env,
        timeout=180,
    )


def test_throwaway_session_records_without_touching_live_lore(
    isolated_gateway,
):
    project, port, env = isolated_gateway
    live_before = live_project_paths()
    assert str(project) not in live_before

    result = run_throwaway_session(project, port, env)
    assert result.returncode == 0, result.stderr or result.stdout
    events = [json.loads(line) for line in result.stdout.splitlines()]
    text = "".join(
        event["part"]["text"] for event in events if event.get("type") == "text"
    )
    assert text == "OK", result.stdout

    sessions: list[dict] = []
    for _ in range(30):
        recorded = run(
            [
                LORE,
                "data",
                "list",
                "sessions",
                "--project",
                str(project),
                "--json",
            ],
            env=env,
            timeout=30,
        )
        assert recorded.returncode == 0, recorded.stderr
        sessions = json.loads(recorded.stdout or "[]")
        if (
            sessions
            and sessions[0].get("message_count", 0) >= 2
            and sessions[0].get("undistilled_count", 0) >= 2
        ):
            break
        time.sleep(0.5)

    assert sessions, (
        "the gateway proxied the call but recorded no session in its isolated "
        f"database. opencode output: {result.stdout[:500]}"
    )
    assert sessions[0]["message_count"] >= 2, sessions[0]
    assert sessions[0]["undistilled_count"] >= 2, sessions[0]
    assert str(project) not in live_project_paths()
