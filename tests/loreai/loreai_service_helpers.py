"""Shared rendering helpers for Lore service seam tests."""

from __future__ import annotations

import os
from pathlib import Path
import plistlib
import re
import shlex
import subprocess

import jinja2

ROOT = Path(__file__).resolve().parents[2]
TOPIC = ROOT / "dotfiles" / "apps" / "loreai"
JINJA = jinja2.Environment(undefined=jinja2.StrictUndefined)
JINJA.tests["match"] = lambda value, pattern: re.match(str(pattern), str(value))


def render(template_name: str, **variables) -> str:
    template = JINJA.from_string((TOPIC / "templates" / template_name).read_text())
    return template.render(**variables)


def render_env_file() -> str:
    return render(
        "loreai-env.zsh.j2",
        ansible_date_time={"date": "2026-10-27"},
        loreai_telemetry_final=1,
        loreai_inference_final="openrouter",
        loreai_local_upstream="http://localhost:11434",
        loreai_worker_model_final="openrouter/z-ai/glm-5.3-flash",
        loreai_worker_model_candidates=[],
        loreai_worker_model_local_candidates=[],
    )


def service_command(tmp_path, manager: str) -> tuple[list[str], str]:
    """Return the command a rendered service manager would run."""
    env_file = tmp_path / "env.zsh"
    env_file.write_text('export OPENROUTER_API_KEY="$(llm keys get openrouter)"\n')
    variables = {
        "loreai_env_file": str(env_file),
        "loreai_install_dir": str(tmp_path),
        "loreai_service_path": f"{tmp_path / 'bin'}:{os.defpath}",
        "loreai_gateway_label": "ai.withlore.gateway",
        "loreai_logs_dir": str(tmp_path),
    }
    if manager == "launchd":
        document = render("lore-gateway.plist.j2", **variables)
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE'
            + document.split("<!DOCTYPE", 1)[1]
        )
        plist = plistlib.loads(body.encode())
        return plist["ProgramArguments"], plist["EnvironmentVariables"]["PATH"]

    document = render("lore-gateway.service.j2", **variables)
    exec_start = next(
        line for line in document.splitlines() if line.startswith("ExecStart=")
    )
    # systemd turns $$ into a literal dollar before invocation.
    command = shlex.split(exec_start.removeprefix("ExecStart=").replace("$$", "$"))
    path = next(
        line.removeprefix('Environment="PATH=').removesuffix('"')
        for line in document.splitlines()
        if line.startswith('Environment="PATH=')
    )
    return command, path


def run_service_command(tmp_path, manager):
    """Execute a rendered launch command with stub binaries."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    llm = bin_dir / "llm"
    llm.write_text("#!/bin/sh\nprintf 'dummy-openrouter-key\\n'\n")
    llm.chmod(0o755)
    lore = tmp_path / "lore"
    lore.write_text(
        "#!/bin/sh\n"
        '[ "$1" = start ] && [ "$2" = --local ] '
        '&& [ "$OPENROUTER_API_KEY" = dummy-openrouter-key ] '
        '&& [ "$LORE_WORKER_API_KEY" = dummy-openrouter-key ]\n'
    )
    lore.chmod(0o755)
    command, path = service_command(tmp_path, manager)

    return subprocess.run(
        command,
        env={"HOME": str(tmp_path), "PATH": path},
        capture_output=True,
        text=True,
        check=False,
    )
