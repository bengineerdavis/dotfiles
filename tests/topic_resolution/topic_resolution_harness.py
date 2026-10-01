"""Paths, plays and assertions shared by the topic-resolution tests.

Deliberately not conftest.py, for the same reason guards' harness is not: every
conftest is imported as a top-level module named `conftest`, so `from conftest
import ...` would resolve to whichever conftest pytest imported first. A second
conftest anywhere else in the run silently rewires the import.

The role under test reads two host facts — `resolution_topic_metadata` and
`resolution_os_family` — so both harness plays are nearly empty: they import
`roles/topic-resolution` and leave the rest to `-e` (synthetic metadata) or to
inline discovery (real metadata). The play is always run bare (no `--tags`), so
the map tasks, the PATH probe and the strict assert run together.
"""

from __future__ import annotations

import pathlib


REPO = pathlib.Path(__file__).resolve().parents[2]
DOTFILES = REPO / "dotfiles"
ROLE = DOTFILES / "roles" / "topic-resolution"
DEFAULTS = ROLE / "defaults" / "main.yaml"

HARNESS = """\
- name: "topic-resolution under test"
  hosts: localhost
  connection: local
  gather_facts: false
  become: false
  tasks:
    - name: "import the resolver"
      ansible.builtin.import_role:
        name: "roles/topic-resolution"
"""

# Real-metadata harness: runs the same discovery the parent playbook uses —
# find apps/*/topic.yml, slurp each, b64decode, from_yaml — then imports the
# role. `resolution_os_family` and `topic_apps_dir` are supplied via -e.
DISCOVERY_HARNESS = """\
- name: "topic-resolution against real topic metadata"
  hosts: localhost
  connection: local
  gather_facts: false
  become: false
  tasks:
    - name: "Find all topic.yml files"
      ansible.builtin.find:
        paths: "{{ topic_apps_dir }}/apps"
        patterns:
          - "topic.yml"
          - "topic.yaml"
        recurse: true
        depth: 2
        file_type: file
      register: meta_find_result

    - name: "Collect topic.yml paths (sorted)"
      ansible.builtin.set_fact:
        topic_meta_paths: "{{ meta_find_result.files | map(attribute='path') "
        "| list | sort }}"

    - name: "Load each topic.yml"
      ansible.builtin.slurp:
        src: "{{ item }}"
      register: topic_meta_reads
      loop: "{{ topic_meta_paths }}"
      loop_control:
        label: "{{ item | dirname | basename }}"

    - name: "Build resolution_topic_metadata (all topics in apps/)"
      ansible.builtin.set_fact:
        resolution_topic_metadata: >-
          {{
            topic_meta_reads.results
            | map(attribute='content')
            | map('b64decode')
            | map('from_yaml')
            | list
          }}

    - name: "Resolve topic dependencies"
      ansible.builtin.import_role:
        name: "roles/topic-resolution"
"""


def said(result, phrase: str) -> bool:
    """Whether the run's output contains `phrase`, ignoring line wrapping.

    Ansible hard-wraps task output for the terminal, so a phrase that reads as
    one sentence in the source can arrive split across a newline in stdout.
    Asserting on raw text would make the test pass or fail on where the wrap
    lands, which is not a property of the role at all.
    """

    def collapse(s: str) -> str:
        return " ".join(s.split())

    return collapse(phrase) in collapse(result.stdout)
