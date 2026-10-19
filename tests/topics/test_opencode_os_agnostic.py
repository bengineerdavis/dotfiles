"""Guard that the opencode topic's lifecycle tasks stay OS-agnostic.

opencode installs on both macOS and Debian, and its cross-OS behaviour must
come from resolving `brew`/`npx` off PATH plus the dependency resolver, never
from an OS branch inside the topic or a hard-coded brew prefix. A hard-coded
prefix breaks one of the two OSes silently — macOS Intel is `/usr/local`,
macOS ARM is `/opt/homebrew`, and linuxbrew is `/home/linuxbrew/.linuxbrew` —
and the failure does not error, it just installs to the wrong place or not at
all. Because `brew` itself resolves the same `community.general.homebrew`
module and `opencode_tap` name on every OS, the only way this topic regresses
is someone adding an OS conditional or a literal path by hand. This test
catches that.

Static, like test_zsh_layout.py: it reads the task files and asserts on their
text and structure. It never runs ansible or touches the deployed tree.

Run:
    pytest tests/topics -v
"""

from __future__ import annotations

import re

# pyrefly: ignore [missing-import]
from payload_seam import PAYLOAD_ROOT

TOPIC = PAYLOAD_ROOT / "dotfiles" / "apps" / "opencode"
TASKS = TOPIC / "tasks"

# The five lifecycle files the topic router (tasks/main.yaml) imports. A
# missing one breaks the router before any OS question arises.
CRUD_FILES = ["bootstrap", "prerequisites", "install", "upgrade", "remove"]

# A literal brew prefix bakes one machine's layout into the task. Asserting
# these never appear keeps install/remove resolving `brew` off PATH instead.
BREW_PREFIXES = (
    "/opt/homebrew",
    "/usr/local/bin/brew",
    "/usr/local/opt",
    "/home/linuxbrew",
    "homebrew_bin",
)


def _read(name: str) -> str:
    """Task file text; the file is known to exist only after test_crud_files_exist."""
    return (TASKS / f"{name}.yaml").read_text()


def _code(text: str) -> str:
    """Full-line comment lines dropped, code and blank lines kept.

    A comment explaining *why* a prefix is not hard-coded (e.g. naming
    `/opt/homebrew` as the thing to avoid) must not trip the prefix check.
    Inline comments on a code line are harder to strip, so the prefix check
    scans this comment-stripped text and the other assertions prefer FQCN
    presence and structure over substring hunting.
    """
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )


def test_crud_files_exist():
    """Every lifecycle file the router imports is present."""
    missing = [name for name in CRUD_FILES if not (TASKS / f"{name}.yaml").is_file()]
    assert not missing, (
        "opencode lifecycle file(s) missing — the topic router imports all five, "
        f"so one gone breaks install on both OSes: {missing}"
    )


def test_no_os_family_branch():
    """install/upgrade/remove must not branch on the OS.

    The topic's cross-OS behaviour comes from `brew`/`npx` resolving off PATH
    and the dependency resolver. A `when:` keyed on `os_family` (or the
    `ansible_facts['os_family']` spelling) hard-codes one OS's path inside the
    topic, which is exactly the regression this guards.
    """
    offenders = {}
    for name in ("install", "upgrade", "remove"):
        code = _code(_read(name))
        if "os_family" in code:
            offenders[name] = code
    assert not offenders, (
        "OS conditional(s) found in opencode task file(s): "
        + ", ".join(sorted(offenders))
        + ". Cross-OS behaviour must come from resolving brew/npx off PATH, "
        "not an os_family branch in the topic."
    )


def test_no_hardcoded_brew_prefix():
    """install/remove never reference a literal brew prefix path."""
    offenders = {}
    for name in ("install", "remove"):
        code = _code(_read(name))
        hits = [prefix for prefix in BREW_PREFIXES if prefix in code]
        if hits:
            offenders[name] = hits
    assert not offenders, (
        "hard-coded brew prefix(es) found in opencode task file(s): "
        + ", ".join(
            f"{name} -> {', '.join(hits)}" for name, hits in sorted(offenders.items())
        )
        + ". Use `brew` (resolved off PATH) or the community.general.homebrew "
        "modules; a literal prefix breaks one of Darwin-Intel, Darwin-ARM, or "
        "linuxbrew."
    )


def test_topic_declares_both_oses():
    """topic_os names both OSes — the cross-OS claim is only true if it does."""
    text = (TOPIC / "topic.yml").read_text()
    match = re.search(r"^topic_os:\s*\[([^\]]*)\]", text, re.MULTILINE)
    assert match, "opencode topic.yml is missing a topic_os: [...] line"
    listed = {os_name.strip().strip("'\"") for os_name in match.group(1).split(",")}
    assert listed == {"Darwin", "Debian"}, (
        f"opencode topic_os = {sorted(listed)}; expected [Darwin, Debian] — "
        "the cross-OS install method is only claimed for the OSes declared here."
    )


def test_install_uses_homebrew_module_with_pinned_tap():
    """The binary install is the community.general.homebrew module on a name
    from defaults/main.yaml (opencode_tap) — the same tap on both OSes.

    Retargeted for the v2 migration: the install task installs
    `{{ opencode_tap }}/opencode-v2`. The v1 name now belongs only to the
    conflict-clearing uninstall, whose presence and ordering are asserted
    with task structure in test_opencode_v2_tasks.py.

    This is also the counterweight: it fails if the brew install is renamed or
    removed, so the vacuous-pass failure mode (every task stripped) goes red.
    """
    code = _code(_read("install"))
    assert "community.general.homebrew:" in code, (
        "opencode install.yaml no longer installs via community.general.homebrew; "
        "the binary install is what must stay OS-agnostic."
    )
    v2_name = (
        'name: "{{ opencode_tap }}/opencode-v2"' in code
        or 'name: "anomalyco/tap/opencode-v2"' in code
    )
    assert v2_name, (
        'opencode install.yaml does not install "{{ opencode_tap }}/'
        'opencode-v2" from the pinned opencode_tap default; a hard-coded '
        "formula name would let one OS fall to the same-named homebrew/core "
        "formula, and installing the v1 name again would undo the migration."
    )
    defaults = (TOPIC / "defaults" / "main.yaml").read_text()
    assert "opencode_tap:" in defaults, (
        "opencode_tap is missing from defaults/main.yaml; the tap is the one "
        "value shared by both OSes."
    )


def test_remove_uninstalls_via_homebrew_module():
    """remove.yaml carries the community.general.homebrew uninstall counterpart."""
    code = _code(_read("remove"))
    assert "community.general.homebrew:" in code and "state: absent" in code, (
        "opencode remove.yaml no longer uninstalls via community.general.homebrew "
        "with state: absent; the CRUD teardown must mirror the OS-agnostic install."
    )
