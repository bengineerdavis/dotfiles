"""Ansible-owned destinations must be declared, not merely absent.

`chezmoi unmanaged ~/.config` reported `.config/loreai`, and nothing in the
repo said why. The answer is that apps/loreai's first-install prompts write
`~/.config/loreai/env.zsh` from `templates/loreai-env.zsh.j2`, so Ansible owns
that file and chezmoi must never write it. That arrangement was recorded only
by the absence of a source file — the weakest possible evidence, and the one
state a future session cannot tell apart from "nobody has thought about this
yet". The file also holds the live OpenRouter key at mode 0600 inside a 0700
directory, so an accidental adoption (someone dropping a source file at
`dot_config/loreai/`) would render a template over a secret.

The check asks chezmoi rather than parsing `.chezmoiignore`. A test that
reimplemented the matcher would agree with itself while chezmoi disagreed —
the same trap `test_governance_not_deployed` documents. It also asserts a
path that is NOT declared stays unmanaged in the same run, because "no paths
are unmanaged" would be satisfied by an ignore file broad enough to deploy
nothing at all.

Reading `unmanaged` rather than `managed` is deliberate. `managed` already
omits `.config/loreai` today, so an assertion against it would pass before
the declaration existed and prove nothing. `unmanaged` is the command whose
answer actually changes: one loreai hit without the rule, zero with it.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

pytestmark = pytest.mark.skipif(
    shutil.which("chezmoi") is None, reason="chezmoi not installed"
)

# The declared destination, and a decoy the payload does not declare. The
# decoy is the non-vacuity guard: it must still appear in `unmanaged`.
DECLARED = ".config/loreai"
UNDECLARED = ".config/ansible-owned-path-test-decoy"


def unmanaged_in(disposable_home, *paths: str) -> set[str]:
    """Ask the real payload what it leaves unmanaged in a disposable home.

    The source is the payload seam and only the destination is disposable,
    so the answer describes this repo's ignore rules rather than a fixture's.
    """
    target = disposable_home / "home"
    for rel in paths:
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")

    out = subprocess.run(
        ["chezmoi", "-S", str(PAYLOAD_ROOT), "-D", str(target), "unmanaged"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert out.returncode == 0, f"chezmoi unmanaged failed: {out.stderr}"
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


def test_ansible_owned_destination_is_declared(tmp_path):
    """`~/.config/loreai` is Ansible-owned, so chezmoi must not call it unmanaged."""
    found = unmanaged_in(tmp_path, f"{DECLARED}/env.zsh", f"{UNDECLARED}/thing.conf")

    # The guard first: if this fails, the ignore rules have swallowed a path
    # nothing declares and the assertion below means nothing.
    assert UNDECLARED in found, (
        f"{UNDECLARED} is not reported as unmanaged — the ignore rules are too "
        "broad for this check to prove anything"
    )
    assert DECLARED not in found, (
        f"{DECLARED} is reported as unmanaged. apps/loreai writes that path at "
        "first install (tasks/prompts.yaml), so chezmoi must never deploy it. "
        "Declare it in home/.chezmoiignore under the Ansible-owned block: both "
        f"'{DECLARED}' and '{DECLARED}/**'."
    )
