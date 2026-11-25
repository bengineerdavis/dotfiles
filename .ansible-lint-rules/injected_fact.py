"""Catch bare top-level fact vars: the INJECT_FACTS_AS_VARS deprecation.

ansible-core 2.24 stops injecting facts as top-level vars, so
`ansible_env`, `ansible_hostname`, `ansible_date_time` and
`ansible_user_dir` stop resolving there. ansible-lint's own
`deprecations` rules do not cover this class: measured 2026-11-09, a
play reading `{{ ansible_env.HOME }}` passed clean at the `production`
profile.

Scans file content rather than task arguments, because most references
live in role defaults, vars and templates that `matchtask` never sees.
Measured 2026-11-09: a `matchtask` version found 10 of this tree's 37
references, while this one found all of them.
"""

from __future__ import annotations

import re
from typing import Any

from ansiblelint.rules import AnsibleLintRule

# `ansible_*` names that are NOT facts, so they survive 2.24 unchanged.
MAGIC = frozenset(
    {
        "ansible_check_mode",
        "ansible_config_file",
        "ansible_diff_mode",
        "ansible_failed_result",
        "ansible_index_var",
        "ansible_inventory_sources",
        "ansible_loop",
        "ansible_loop_var",
        "ansible_managed",
        "ansible_password",
        "ansible_play_hosts",
        "ansible_playbook_python",
        "ansible_python_interpreter",
        "ansible_role_name",
        "ansible_run_tags",
        "ansible_skip_tags",
        "ansible_verbosity",
        "ansible_version",
    }
)

# The supported form is not a fact var. The rule's first version
# reported it, which is why a negative test case exists.
ALLOWED = MAGIC | {"ansible_facts"}

# A bare reference: preceded by neither a word character nor a dot,
# so `ansible_facts['env']` and `not_ansible_env` do not match.
PATTERN = re.compile(r"(?<![\w.])ansible_[a-z][a-z0-9_]*")


class InjectedFactRule(AnsibleLintRule):
    """Bare top-level fact vars are deprecated in ansible-core 2.24."""

    id = "injected-fact-vars"
    description = (
        "Use ansible_facts[...] instead of a bare top-level fact var; "
        "injecting facts as top-level vars is removed in ansible-core 2.24"
    )
    severity = "HIGH"
    tags = ["deprecations"]
    version_changed = "0.0.1"

    def matchyaml(self, file: Any) -> list:
        text = getattr(file, "content", None)
        if text is None:
            return []
        matches = []
        for lineno, line in enumerate(text.splitlines(), 1):
            # A prose mention in a comment is not a template expression,
            # and the repo's comments discuss these names deliberately.
            code = line.split("#", 1)[0]
            bad = sorted({m.group(0) for m in PATTERN.finditer(code)} - ALLOWED)
            if not bad:
                continue
            matches.append(
                self.create_matcherror(
                    message=(
                        f"bare top-level fact var(s) {bad}; "
                        "use ansible_facts[...] instead"
                    ),
                    lineno=lineno,
                    filename=file,
                    tag=f"deprecations[{self.id}]",
                )
            )
        return matches
