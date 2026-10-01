"""The global opencode template renders a valid, correctly layered config.

Models, providers and agents come from .chezmoidata/opencode.yaml, merged as
common -> os.<os> -> hosts.<hostname>. The permission block stays literal in
the template because its rules are order-sensitive (last match wins) and a
data merge would sort them. These tests render the template with chezmoi
under overridden host/os data, so they exercise the real merge, not a copy.

Run:
    pytest tests/topics/test_opencode_config_layers.py -v
"""

from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TEMPLATE = REPO / "dot_config" / "opencode" / "opencode.jsonc.tmpl"

pytestmark = pytest.mark.skipif(
    shutil.which("chezmoi") is None, reason="chezmoi not on PATH"
)


def _strip_jsonc(text: str) -> str:
    """Drop // line comments outside strings, then trailing commas."""
    out = []
    for line in text.splitlines():
        in_str = False
        cut = len(line)
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "\\" and in_str:
                i += 2
                continue
            if ch == '"':
                in_str = not in_str
            elif not in_str and line.startswith("//", i):
                cut = i
                break
            i += 1
        out.append(line[:cut])
    return re.sub(r",(\s*[}\]])", r"\1", "\n".join(out))


def render(hostname: str, os_name: str, extra: dict | None = None) -> dict:
    data = {"chezmoi": {"hostname": hostname, "os": os_name}}
    if extra:
        data.update(extra)
    result = subprocess.run(
        [
            "chezmoi",
            "-S",
            str(REPO),
            "execute-template",
            "--override-data",
            json.dumps(data),
        ],
        input=TEMPLATE.read_text(),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(_strip_jsonc(result.stdout))


@pytest.mark.parametrize(
    "hostname,os_name", [("L37V3P6GQ3", "darwin"), ("unlisted-box", "linux")]
)
def test_renders_deep_agent_on_both_oses(hostname, os_name):
    cfg = render(hostname, os_name)
    deep = cfg["agent"]["deep"]
    assert deep["model"] == "openrouter/anthropic/claude-opus-5"
    assert deep["variant"] == "max"
    variants = cfg["provider"]["openrouter"]["models"]["anthropic/claude-opus-5"][
        "variants"
    ]
    assert variants["max"] == {"reasoning": {"effort": "max"}}
    assert cfg["model"] == "openrouter/z-ai/glm-5.3-flash"


def test_os_then_host_layers_override_common():
    overlay = {
        "opencode": {
            "os": {"linux": {"small_model": "ollama/os-layer"}},
            "hosts": {"box": {"agent": {"deep": {"variant": "xhigh"}}}},
        }
    }
    box = render("box", "linux", overlay)
    assert box["small_model"] == "ollama/os-layer"
    assert box["agent"]["deep"]["variant"] == "xhigh"
    # Deep merge: the host override keeps the sibling keys from common.
    assert box["agent"]["deep"]["model"] == "openrouter/anthropic/claude-opus-5"

    other = render("other", "linux", overlay)
    assert other["agent"]["deep"]["variant"] == "max"

    mac = render("box", "darwin", overlay)
    assert mac["small_model"] == "ollama/qwen3:8b"


def test_bash_catch_all_stays_first():
    """The data merge must not touch the order-sensitive permission block."""
    cfg = render("L37V3P6GQ3", "darwin")
    assert list(cfg["permission"]["bash"])[0] == "*"
    assert list(cfg["permission"]["external_directory"])[0] == "*"
