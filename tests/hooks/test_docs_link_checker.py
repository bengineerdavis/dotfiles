"""Select documentation links without weakening the egress boundary."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tomllib

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "check-docs-links.py"
spec = importlib.util.spec_from_file_location("check_docs_links", SCRIPT)
assert spec and spec.loader
links = importlib.util.module_from_spec(spec)
spec.loader.exec_module(links)


def hook(hook_id: str) -> dict:
    config = tomllib.loads((REPO / "prek.toml").read_text())
    return next(
        hook
        for repo in config["repos"]
        for hook in repo.get("hooks", [])
        if hook.get("id") == hook_id
    )


@pytest.mark.parametrize(
    "path",
    [
        ".lore.md",
        "backlog/tasks/DOT-1.md",
        "changelog.d/fragment.md",
        "CHANGELOG.md",
        "home/bin/executable_READMD.archive.md",
        "home/dotfiles/apps/ollama/docs/RESEARCH.md",
        "scripts/README.txt",
        "../outside.md",
    ],
)
def test_excluded_documents_are_never_selected(path: str):
    assert not links.is_selected(path)


def test_full_scan_uses_tracked_markdown_and_never_dot(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("[local](target.md)")
    (tmp_path / ".lore.md").write_text("[private](https://example.com)")
    (tmp_path / "untracked.md").write_text("[broken](missing.md)")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "docs/guide.md", ".lore.md"], check=True
    )
    assert links.tracked_markdown(tmp_path) == ["docs/guide.md"]


def test_offline_command_cannot_make_network_requests():
    command = links.lychee_command(["docs/guide.md"], external=False)
    assert "--offline" in command
    assert "--offline=false" not in command
    assert command[-2:] == ["--files-from", "-"]


def test_external_mode_is_explicit_and_not_an_unattended_hook():
    assert "--external" in links.USAGE
    assert hook("docs-links-local")["entry"].endswith("--changed")
    assert hook("docs-links-full")["stages"] == ["pre-push"]
    assert "--external" not in hook("docs-links-local")["entry"]
    assert "--external" not in hook("docs-links-full")["entry"]


def test_external_mode_requires_explicit_approval(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("LYCHEE_EXTERNAL_APPROVED", raising=False)
    with pytest.raises(SystemExit) as error:
        links.parse_args(["--external", "--changed"])
    assert error.value.code == 2


def test_unapproved_external_run_does_not_invoke_lychee(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv("LYCHEE_EXTERNAL_APPROVED", raising=False)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Lychee ran without approval")

    monkeypatch.setattr(links.subprocess, "run", fail_if_called)
    assert links.main(["--external"]) == 2


def test_real_lychee_detects_broken_local_link(tmp_path: Path):
    """The one test that needs an actual Lychee binary.

    Skipped rather than failed when no backend can run. This is the
    honest form of "cannot run here": the suite still asserts the
    selection logic in the tests above, and this one states plainly
    that the binary was absent instead of reporting a false failure.
    CI has neither mise nor a Lychee backend, which is why this is
    skipped there — measured 2026-11-05.
    """
    if links.select_backend() is None:
        pytest.skip(
            "no Lychee backend available — install it with "
            "`mise install cargo:lycheeverse/lychee`"
        )
    document = tmp_path / "broken.md"
    document.write_text("[missing](missing.md)\n")
    result = subprocess.run(
        [*links.lychee_command([str(document)], external=False)[:-2], str(document)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode != 0
    assert "missing.md" in result.stdout + result.stderr


def test_changed_scope_does_not_expand_to_the_whole_repository():
    args = links.parse_args(["--changed", "docs/guide.md"])
    assert args.changed
    assert args.files == ["docs/guide.md"]


def test_no_executable_backend_fails_loudly_instead_of_skipping(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    """A checker that cannot run must not report success.

    A skip and a pass look identical in a commit log, so returning 0
    here would let every future docs commit through unchecked.
    Measured 2026-11-04: the aqua binary could not execute at all, and
    the commit still needed evidence rather than --no-verify.
    """
    # The subject is the backend probe, not whether this host has
    # mise. CI has neither mise nor a backend, and `main` checks
    # for mise first — which returns 2 for the wrong reason and
    # passes the test without exercising the message under test.
    monkeypatch.setattr(links.shutil, "which", lambda _: "/usr/bin/mise")
    monkeypatch.setattr(links, "BACKENDS", ("cargo:lycheeverse/lychee",))
    monkeypatch.setattr(links, "probe_backend", lambda token: False)
    code = links.main(["--changed", "docs/TOPIC-RECIPES.md"])
    assert code == 2
    err = capsys.readouterr().err
    assert "No Lychee backend could be executed" in err
    assert "cargo:lycheeverse/lychee" in err


def test_a_backend_that_runs_is_not_replaced_when_it_finds_broken_links(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Fall through on failure-to-execute; never on a finding.

    The distinction is the whole safety property. If a broken link
    caused a retry, the second backend could pass and the finding
    would vanish.
    """
    attempted: list[list[str]] = []
    (tmp_path / "guide.md").write_text("[broken](missing.md)\n")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "guide.md"], check=True)

    def record(command, **kwargs):
        attempted.append(command)
        if command[:2] == ["git", "-C"]:
            return subprocess.CompletedProcess(command, 0, stdout=b"guide.md\0")
        # First backend runs and fails the link; the second would pass.
        code = 2 if "cargo:lycheeverse/lychee" in " ".join(command) else 0
        return subprocess.CompletedProcess(command, code, stdout=b"")

    monkeypatch.setattr(links, "CONFIG", tmp_path / "lychee.toml")
    (tmp_path / "lychee.toml").write_text("offline = true\n")
    monkeypatch.setattr(links.shutil, "which", lambda _: "/usr/bin/mise")
    monkeypatch.setattr(links.subprocess, "run", record)
    monkeypatch.setattr(links, "probe_backend", lambda token: True)
    code = links.main(["--changed", "guide.md"], repo=tmp_path)
    assert code == 2, "the broken-link result must stand"
    link_calls = [cmd for cmd in attempted if "--files-from" in cmd]
    assert len(link_calls) == 1, f"fell through on a finding: {link_calls}"
    assert "cargo:lycheeverse/lychee" in link_calls[0]


def test_changed_scope_only_checks_selected_tracked_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("[local](target.md)")
    (tmp_path / "other.md").write_text("[broken](missing.md)")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    calls: list[tuple[list[str], dict]] = []

    def record(command, **kwargs):
        calls.append((command, kwargs))
        stdout = b"docs/guide.md\0" if command[:2] == ["git", "-C"] else None
        return subprocess.CompletedProcess(command, 0, stdout=stdout)

    monkeypatch.setattr(links, "CONFIG", tmp_path / "lychee.toml")
    (tmp_path / "lychee.toml").write_text("offline = true\n")
    monkeypatch.setattr(links.shutil, "which", lambda _: "/usr/bin/mise")
    monkeypatch.setattr(links.subprocess, "run", record)
    monkeypatch.setattr(links, "probe_backend", lambda token: True)
    assert links.main(["--changed", "docs/guide.md"], repo=tmp_path) == 0
    # A version probe runs first, so match the link check by its
    # stdin rather than as "the only subprocess call".
    lychee_calls = [(cmd, kw) for cmd, kw in calls if "--files-from" in cmd]
    assert len(lychee_calls) == 1
    command, kwargs = lychee_calls[0]
    assert "--offline" in command
    assert kwargs["input"] == "docs/guide.md\n"
    assert "other.md" not in kwargs["input"]
