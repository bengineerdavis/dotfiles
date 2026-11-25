"""The ansible-lint gate catches bare top-level fact vars, and relents elsewhere.

Ansible-core 2.24 stops injecting facts as top-level vars, so `ansible_env`,
`ansible_hostname`, `ansible_date_time` and `ansible_user_dir` stop resolving.
Three mechanisms were measured on 2026-11-09 and 2026-11-24 and none catches
this class:

- `ansible-lint 26.11.0 --strict` passes a play reading `{{ ansible_env.HOME }}`
  clean at the `production` profile. Its five `deprecations`-tagged rules are
  `deprecated-bare-vars`, `deprecated-local-action`, `deprecated-module`,
  `no-jinja-when` and `role-name`; none covers injected fact vars.
- `ansible-playbook` has no fail-on-deprecation flag, and `--syntax-check` does
  not template, so it never reaches the expression.
- Setting `inject_facts_as_vars = False` makes the run fail loudly, but a lint
  run still passes: lint never templates role defaults. Measured 2026-11-24 by
  linting `apps/backlog/defaults/main.yaml` with the flip in place — clean.

So the gate is a custom rule loaded through `rulesdir`. These tests prove it
fires on the deprecated form and stays silent on everything else, which is the
property a rule that matches nothing would also "pass".

Why a subprocess rather than importing the rule: the contract under test is
that the repo's `.ansible-lint` actually wires the rule in. Importing the
class would test the class while leaving the wiring — the part that silently
broke during development — untested.

The config sits at the repo root, outside the payload, so the lint tooling
never reaches a target machine's `~/dotfiles`. ansible-lint walks up to find
it; the runs below therefore use `home/dotfiles` as the working directory,
which is where the Ansible project root is and where role paths resolve.
"""

from __future__ import annotations

import re
import shutil
import subprocess

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT
import pytest

DOTFILES = PAYLOAD_ROOT / "dotfiles"
CONFIG = PAYLOAD_ROOT.parent / ".ansible-lint"

pytestmark = pytest.mark.skipif(
    shutil.which("ansible-lint") is None,
    reason="ansible-lint not on PATH",
)

# The rule id, as the config's `enable_list` names it and as it appears in
# output. Kept as one constant so a rename cannot half-land.
RULE_ID = "injected-fact-vars"

# Deprecated spellings, one per fact class in this tree. The task's census
# found all four in use: ansible_env 31 refs, ansible_hostname 8,
# ansible_user_dir 2, ansible_date_time 1.
DEPRECATED_FORMS = [
    "{{ ansible_env.HOME }}",
    "{{ ansible_hostname }}",
    "{{ ansible_user_dir }}/.cache",
    "{{ ansible_date_time.iso8601 }}",
]


def _lint(tmp_path, body: str) -> subprocess.CompletedProcess[str]:
    """Lint one throwaway playbook against the repo's real lint config.

    The play is written under `tmp_path` so a failure cannot leave the payload
    dirty; the config under test is the repo's, and only the play is
    temporary.

    `-c` is passed explicitly rather than left to discovery because the play
    lives outside the repo, and discovery walks up from the play's location.
    An earlier version wrote a config beside the play instead, which made
    ansible-lint treat `tmp_path` as the project and report "0 files processed
    of 1 encountered" with exit 0 — a silent pass (measured 2026-11-24).

    `cwd=DOTFILES` because that is the Ansible project root. Running from the
    repo root instead resolves `role: apps/<topic>` imports against the wrong
    directory and reports 43 spurious `syntax-check[specific]` failures
    (measured 2026-11-25).
    """
    play = tmp_path / "play.yml"
    play.write_text(body, encoding="utf-8")
    return subprocess.run(
        [
            "ansible-lint",
            "-c",
            str(CONFIG),
            "-f",
            "pep8",
            str(play),
        ],
        cwd=DOTFILES,
        capture_output=True,
        text=True,
        check=False,
    )


def _play(*messages: str) -> str:
    tasks = "\n".join(
        f"    - name: task {i}\n"
        "      ansible.builtin.debug:\n"
        f'        msg: "{message}"\n'
        for i, message in enumerate(messages)
    )
    return (
        "---\n"
        "- name: probe\n"
        "  hosts: localhost\n"
        "  gather_facts: false\n"
        "  tasks:\n" + tasks
    )


@pytest.mark.parametrize("expression", DEPRECATED_FORMS)
def test_a_bare_top_level_fact_is_reported(tmp_path, expression):
    result = _lint(tmp_path, _play(expression))

    assert RULE_ID in result.stdout, (
        f"the gate did not report {expression!r}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    # A message naming the var is what makes the finding actionable; the rule
    # id alone would not tell a reader which expression to change.
    assert "ansible_facts[" in result.stdout


def test_the_supported_form_is_not_reported(tmp_path):
    result = _lint(tmp_path, _play("{{ ansible_facts['env']['HOME'] }}"))

    assert RULE_ID not in result.stdout, (
        "the gate reported the supported ansible_facts[...] form, so it would "
        f"fire on every file after the migration.\nstdout:\n{result.stdout}"
    )


def test_magic_vars_are_not_reported(tmp_path):
    """Magic vars are not facts and survive 2.24, so they must pass.

    `inject_facts_as_vars` controls fact injection only. Probed 2026-11-09 with
    the setting off: these stayed defined while `ansible_env` went undefined.
    An over-broad pattern would flag them and the gate would be red for
    reasons nobody could act on.
    """
    result = _lint(
        tmp_path,
        _play(
            "{{ ansible_check_mode }}",
            "{{ ansible_run_tags }}",
            "{{ ansible_managed }}",
            "{{ ansible_python_interpreter }}",
        ),
    )

    assert RULE_ID not in result.stdout, (
        f"the gate reported a magic var.\nstdout:\n{result.stdout}"
    )


def test_a_prose_mention_in_a_comment_is_not_reported(tmp_path):
    """Comments discuss these names deliberately; only code counts.

    `apps/loreai/tasks/registry-answers.yaml:37` and `machines.yml` both carry
    prose about `ansible_env`. Reporting those would make the gate unpassable
    without deleting the explanations.
    """
    body = (
        "---\n"
        "- name: probe\n"
        "  hosts: localhost\n"
        "  gather_facts: false\n"
        "  tasks:\n"
        "    # ansible_env is absent in a facts-less harness, so guard it\n"
        "    - name: quiet\n"
        "      ansible.builtin.debug:\n"
        '        msg: "nothing"\n'
    )
    result = _lint(tmp_path, body)

    assert RULE_ID not in result.stdout, (
        f"the gate reported a prose comment.\nstdout:\n{result.stdout}"
    )


def test_the_config_opts_the_custom_rule_into_the_profile():
    """`profile:` filters rules to its ladder, silently dropping custom ones.

    Measured 2026-11-24: the rule loaded and appeared in `--list-rules` but
    never ran while the config set `profile: basic` without an `enable_list`
    entry. That is a silent pass — the exact failure mode the gate exists to
    prevent — so the wiring is asserted rather than assumed.
    """
    config = CONFIG
    assert config.is_file(), f"{config} is missing, so no rule is wired in"

    text = config.read_text(encoding="utf-8")
    # `enable_list` must name the rule; a comment mentioning it is not enough.
    enabled = re.search(r"^enable_list:\s*\n((?:\s*-\s*\S+\s*\n)*)", text, re.M)
    assert enabled and RULE_ID in enabled.group(1), (
        f"{config} does not enable {RULE_ID}. A custom rule is dropped by the "
        "`profile:` filter unless it is listed under `enable_list`."
    )
