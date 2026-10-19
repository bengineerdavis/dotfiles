"""Paths and assertions shared by the guard tests.

Deliberately not conftest.py: every conftest is imported as a top-level
module named `conftest`, so `from conftest import ...` resolves to whichever
one pytest imported first. With a second conftest anywhere else in the run —
tools/ grew one — the guards' tests silently imported the wrong module.
"""

from __future__ import annotations

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

DOTFILES = PAYLOAD_ROOT / "dotfiles"
GUARDS = DOTFILES / "roles" / "guards"

HARNESS = """\
- name: "guard under test"
  hosts: localhost
  connection: local
  gather_facts: {gather}
  become: false
  tasks:
    - name: "import the guard"
      ansible.builtin.import_role:
        name: "roles/guards"
        tasks_from: {tasks_from}
"""


def said(result, phrase: str) -> bool:
    """Whether the run's output contains `phrase`, ignoring line wrapping.

    Ansible hard-wraps a task's msg for the terminal, so a phrase that reads as
    one sentence in the source arrives split across a newline. Asserting on the
    raw text makes a test pass or fail on where the wrap happens to land, which
    is not a property of the guard at all.
    """

    def collapse(s: str) -> str:
        return " ".join(s.split())

    return collapse(phrase) in collapse(result.stdout)
