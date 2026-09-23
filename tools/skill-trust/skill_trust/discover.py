"""Finding a licence, most specific source first.

Order matters: a permissively licensed skill can sit inside a repository with a
different licence, and the skill's own LICENSE is the truth about that skill.
Falling straight to the repository would get it wrong in both directions.
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess

# A LICENSE file's first lines usually name the licence plainly enough to match.
_TEXT_MARKERS = [
    (re.compile(r"\bMIT License\b", re.I), "MIT"),
    (re.compile(r"\bApache License\b.*2\.0", re.I | re.S), "Apache-2.0"),
    (re.compile(r"\bBSD 3-Clause\b", re.I), "BSD-3-Clause"),
    (re.compile(r"\bBSD 2-Clause\b", re.I), "BSD-2-Clause"),
    (re.compile(r"\bISC License\b", re.I), "ISC"),
    (re.compile(r"\bGNU AFFERO GENERAL PUBLIC LICENSE\b", re.I), "AGPL-3.0"),
    (re.compile(r"\bGNU GENERAL PUBLIC LICENSE\b", re.I), "GPL-3.0"),
    (re.compile(r"\bMozilla Public License Version 2\.0\b", re.I), "MPL-2.0"),
    (re.compile(r"\bBusiness Source License\b", re.I), "BUSL-1.1"),
    (re.compile(r"\bFunctional Source License\b", re.I), "FSL-1.1"),
    (re.compile(r"\bServer Side Public License\b", re.I), "SSPL-1.0"),
    (re.compile(r"\bElastic License\b.*2\.0", re.I | re.S), "Elastic-2.0"),
]

_SPDX_LINE = re.compile(r"SPDX-License-Identifier:\s*([A-Za-z0-9.\-+]+)")
# Deliberately the whole rest of the line, not a single token. Skills in the
# wild write prose in this field — Anthropic's are `Proprietary. LICENSE.txt
# has complete terms`. Anchoring on end-of-line after one token made that match
# nothing, so a skill that declared itself proprietary was reported as carrying
# no licence at all. "None declared" and "declared, and it is proprietary" are
# different facts, and a human chasing the first should not be handed the second.
_FRONTMATTER_LICENCE = re.compile(r"^license:\s*(\S.*?)\s*$", re.M)

# A bare SPDX id, as opposed to a sentence that begins with one.
_SPDX_TOKEN = re.compile(r"^[A-Za-z0-9.\-+]+$")


def normalise_licence(value: str) -> str:
    """Reduce a declared licence field to something classifiable.

    A bare id passes through untouched. Prose is cut at the first sentence or
    clause boundary, which is enough to recover `Proprietary` from Anthropic's
    wording without pretending to parse English.
    """
    value = value.strip()
    if _SPDX_TOKEN.match(value):
        return value
    head = value.split(".", 1)[0].split(",", 1)[0].strip()
    return head or value


def licence_from_dir(path: pathlib.Path) -> str | None:
    """A licence declared by the skill directory itself, or None."""
    if not path.is_dir():
        return None

    skill_md = path / "SKILL.md"
    if skill_md.is_file():
        head = skill_md.read_text(encoding="utf-8", errors="replace")[:4000]
        for pattern in (_SPDX_LINE, _FRONTMATTER_LICENCE):
            found = pattern.search(head)
            if found:
                return normalise_licence(found.group(1))

    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING"):
        candidate = path / name
        if not candidate.is_file():
            continue
        text = candidate.read_text(encoding="utf-8", errors="replace")
        found = _SPDX_LINE.search(text[:2000])
        if found:
            return found.group(1)
        for pattern, spdx in _TEXT_MARKERS:
            if pattern.search(text[:2000]):
                return spdx
    return None


def licence_from_repo(source: str, gh: str | None = None) -> str | None:
    """The repository's licence, via the GitHub CLI.

    Only reached when no explicit rule already decided, so the common path stays
    offline: an approved or banned source never triggers a network call. That is
    deliberate — a checker that phoned home on every run would be unusable on a
    plane and would couple provisioning to GitHub's availability.
    """
    gh = gh or shutil.which("gh")
    if not gh or "/" not in source:
        return None
    try:
        done = subprocess.run(
            [gh, "api", f"repos/{source}", "--jq", ".license.spdx_id"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    return (done.stdout or "").strip() or None
