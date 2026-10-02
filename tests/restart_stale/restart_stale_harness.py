"""Paths and loaders shared by the restart-stale tests.

Deliberately not conftest.py: every conftest is imported as a top-level module
named `conftest`, so `from conftest import ...` resolves to whichever one pytest
imported first. tests/guards/guard_harness.py records the same trap.
"""

from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
DOTFILES = REPO / "dotfiles"
ROLE = DOTFILES / "roles" / "restart-stale"
FILTERS = ROLE / "filter_plugins" / "restart_stale.py"

HARNESS = """\
- name: "restart-stale under test"
  hosts: localhost
  connection: local
  gather_facts: true
  become: false
  tasks:
    - name: "import the role"
      ansible.builtin.import_role:
        name: "roles/restart-stale"
"""


def load_filters():
    """Import the filter plugin as a plain module.

    It is loaded by path rather than put on sys.path because Ansible, not
    Python packaging, owns where it lives: `filter_plugins/` beside the role.
    """
    spec = importlib.util.spec_from_file_location("restart_stale_filters", FILTERS)
    assert spec is not None and spec.loader is not None, (
        f"spec_from_file_location returned None for {FILTERS}"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def said(result, phrase: str) -> bool:
    """Whether the run's output contains `phrase`, ignoring line wrapping."""

    def collapse(s: str) -> str:
        return " ".join(s.split())

    return collapse(phrase) in collapse(result.stdout)
