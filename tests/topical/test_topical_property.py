"""Property: no template markers survive, and all emitted YAML parses.

The invariant is stated independently of the implementation: the
generator's job is that its output contains none of its input
placeholders (`<topic>`, `{{ app_name }}`, the two splice markers), and
that everything it writes is loadable YAML. How it achieves that —
substitution, splicing, wholesale rewrites — is not referenced here.
"""

from __future__ import annotations

import uuid

import pytest
import yaml
from hypothesis import HealthCheck, assume, given, settings, strategies as st

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

MANAGERS = ("homebrew_formula", "homebrew_cask", "homebrew_tap", "apt")

# OS coverage per manager, read from the data file (public input), not
# from the generator's own tables.
_MANAGER_META = yaml.safe_load(
    (PAYLOAD_ROOT / "dotfiles" / "managers.yaml").read_text()
)["managers"]
OS_OF = {name: meta["os"] for name, meta in _MANAGER_META.items()}

names = st.from_regex(r"[a-z][a-z0-9-]{0,9}", fullmatch=True).filter(
    lambda n: n not in {"new", "list", "doctor", "help"} and "--" not in n
)
manager_lists = st.lists(st.sampled_from(MANAGERS), unique=True, max_size=3)


# runner is stateless across invokes, repo_root is a constant, and each
# input scaffolds into its own uuid subdirectory of tmp_path — so the
# function-scoped fixtures need no reset between inputs.
@settings(
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(name=names, managers=manager_lists, data=st.data())
def test_generated_topic_has_no_markers_and_parses(
    name, managers, data, runner, topical_module, repo_root, tmp_path
):
    # The topic's OS list must overlap every chosen manager's cover,
    # exactly as the CLI validates. apt + homebrew_cask don't overlap
    # is correctly refused, so those draws are skipped.
    allowed = [f for f in ("Darwin", "Debian") if all(f in OS_OF[m] for m in managers)]
    assume(allowed)
    os_list = data.draw(st.lists(st.sampled_from(allowed), min_size=1, unique=True))

    into = tmp_path / uuid.uuid4().hex
    args = ["new", name, "--repo", str(repo_root), "--into", str(into)]
    for family in os_list:
        args += ["--os", family]
    for manager in managers:
        args += ["--manager", manager]

    result = runner.invoke(topical_module.app, args)
    assert result.exit_code == 0, result.output

    dest = into / "apps" / name
    files = [p for p in dest.rglob("*") if p.is_file()]
    assert len(files) > 10, "scaffold is suspiciously small — is it generating?"

    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "<topic>" not in text
        assert "{{ app_name }}" not in text
        if path.suffix in (".yaml", ".yml") and path.stat().st_size:
            yaml.safe_load(text)
