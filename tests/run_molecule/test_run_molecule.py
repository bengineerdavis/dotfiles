"""run-molecule.sh argument handling — the wrapper's own contract.

Verified here, cheaply (no VM, no molecule): the verb table and default,
the error paths naming the fix, the chdir and env setup molecule's
scenario discovery and role resolution depend on, collections installed
first, and pass-through of extra molecule args. The molecule run itself
is the scenario's verify phase — a live VM test, not this suite.
"""

from __future__ import annotations

import os
import pathlib
import subprocess

from run_molecule_harness import (
    molecule_invocations,
    molecule_records,
    parse_log,
    run_wrapper,
)

EXPECTED_TAIL = ["-s", "default"]
VERBS = [
    "create",
    "prepare",
    "converge",
    "idempotence",
    "verify",
    "login",
    "destroy",
    "test",
]


def test_default_verb_is_test(scenario_repo: pathlib.Path):
    result = run_wrapper(scenario_repo, "faketopic")
    assert result.returncode == 0, result.stderr
    (argv,) = molecule_invocations(scenario_repo)
    assert argv == [
        "run",
        "--frozen",
        "--project",
        str(scenario_repo),
        "--group",
        "test-vm",
        "molecule",
        "test",
        *EXPECTED_TAIL,
    ]


def test_every_verb_passes_through(scenario_repo: pathlib.Path):
    for verb in VERBS:
        run_wrapper(scenario_repo, "faketopic", verb)
    invocations = molecule_invocations(scenario_repo)
    assert len(invocations) == len(VERBS), "expected one molecule call per verb"
    for verb, argv in zip(VERBS, invocations):
        assert argv == [
            "run",
            "--frozen",
            "--project",
            str(scenario_repo),
            "--group",
            "test-vm",
            "molecule",
            verb,
            *EXPECTED_TAIL,
        ]


def test_unknown_verb_fails_naming_the_valid_ones(scenario_repo: pathlib.Path):
    result = run_wrapper(scenario_repo, "faketopic", "explode")
    assert result.returncode != 0
    assert "unknown verb 'explode'" in result.stderr
    assert "idempotence" in result.stderr, "stderr must name the valid verbs"
    assert molecule_invocations(scenario_repo) == [], "no molecule run on a bad verb"


def test_missing_topic_is_a_usage_error(scenario_repo: pathlib.Path):
    result = run_wrapper(scenario_repo)
    assert result.returncode != 0
    assert "no topic given" in result.stderr
    assert "Usage:" in result.stderr


def test_topic_without_scenario_names_the_path_and_the_fix(
    scenario_repo: pathlib.Path,
):
    result = run_wrapper(scenario_repo, "nosuchtopic")
    assert result.returncode != 0
    assert "dotfiles/apps/nosuchtopic/molecule/default" in result.stderr
    assert "docs/TOPICS.md" in result.stderr


def test_runs_from_any_cwd(scenario_repo: pathlib.Path, tmp_path: pathlib.Path):
    """The wrapper chdirs itself; the caller cwd cannot leak in."""
    caller_cwd = tmp_path / "unrelated"
    caller_cwd.mkdir()
    result = run_wrapper(scenario_repo, "faketopic", cwd=caller_cwd)
    assert result.returncode == 0, result.stderr
    (argv,) = molecule_invocations(scenario_repo)
    assert argv[-1] == "default"  # the run happened (sanity, not cwd proof)
    assert str(caller_cwd) not in " ".join(argv)


def test_molecule_runs_in_the_scenario_parent(
    scenario_repo: pathlib.Path, tmp_path: pathlib.Path
):
    """Scenario discovery is cwd-relative: cwd must be apps/<topic>/."""
    caller_cwd = tmp_path / "unrelated"
    caller_cwd.mkdir()
    result = run_wrapper(scenario_repo, "faketopic", cwd=caller_cwd)
    assert result.returncode == 0, result.stderr
    (record,) = molecule_records(scenario_repo)
    expected = scenario_repo / "home" / "dotfiles" / "apps" / "faketopic"
    assert record["cwd"] == [str(expected)]


def test_project_directory_is_exported(scenario_repo: pathlib.Path):
    """MOLECULE_PROJECT_DIRECTORY points at dotfiles/ for roles."""
    result = run_wrapper(scenario_repo, "faketopic", "converge")
    assert result.returncode == 0, result.stderr
    (record,) = molecule_records(scenario_repo)
    assert record["env-mpd"] == [str(scenario_repo / "home" / "dotfiles")]


def test_collections_path_is_exported(scenario_repo: pathlib.Path):
    """ANSIBLE_COLLECTIONS_PATH points at the user collections dir."""
    result = run_wrapper(scenario_repo, "faketopic", "converge")
    assert result.returncode == 0, result.stderr
    (record,) = molecule_records(scenario_repo)
    (value,) = record["env-acp"]
    assert value == os.path.join(os.environ["HOME"], ".ansible", "collections")


def test_collections_are_installed_first(scenario_repo: pathlib.Path):
    """The collections install precedes the molecule invocation."""
    result = run_wrapper(scenario_repo, "faketopic", "converge")
    assert result.returncode == 0, result.stderr
    records = parse_log(scenario_repo / "uv.log")
    # Three uv calls: the collections install, the driver module path
    # probe, then molecule itself.
    assert len(records) == 3, "expected: ansible-galaxy, python probe, molecule"
    galaxy, probe, molecule = (r["arg"] for r in records)
    assert "ansible-galaxy" in galaxy
    assert "collection" in galaxy and "install" in galaxy
    assert str(scenario_repo / "home" / "dotfiles" / "requirements.yml") in galaxy
    assert "python" in probe and "-c" in probe
    assert "molecule" in molecule


def test_ansible_library_is_exported(scenario_repo: pathlib.Path):
    """ANSIBLE_LIBRARY is the probe stdout: the driver module dir."""
    result = run_wrapper(scenario_repo, "faketopic", "converge")
    assert result.returncode == 0, result.stderr
    records = parse_log(scenario_repo / "uv.log")
    probe = records[1]["arg"]
    assert "python" in probe, "the driver-module probe must run before molecule"
    molecule = records[-1]
    (value,) = molecule["env-al"]
    assert value == "/fake/site-packages/molecule_plugins/vagrant/modules", value


def make_named_scenario(scenario_repo: pathlib.Path, name: str) -> pathlib.Path:
    scenario = (
        scenario_repo / "home" / "dotfiles" / "apps" / "faketopic" / "molecule" / name
    )
    scenario.mkdir(parents=True)
    (scenario / "molecule.yml").touch()
    return scenario


def test_named_scenario_is_passed_to_molecule(scenario_repo, monkeypatch):
    make_named_scenario(scenario_repo, "debian")
    monkeypatch.setenv("MOLECULE_SCENARIO", "debian")
    result = run_wrapper(scenario_repo, "faketopic")
    assert result.returncode == 0, result.stderr
    (argv,) = molecule_invocations(scenario_repo)
    assert argv[-2:] == ["-s", "debian"]


def test_extra_args_pass_through_to_molecule(scenario_repo: pathlib.Path):
    result = run_wrapper(scenario_repo, "faketopic", "test", "--destroy=never")
    assert result.returncode == 0, result.stderr
    (argv,) = molecule_invocations(scenario_repo)
    assert argv == [
        "run",
        "--frozen",
        "--project",
        str(scenario_repo),
        "--group",
        "test-vm",
        "molecule",
        "test",
        *EXPECTED_TAIL,
        "--destroy=never",
    ]


def test_uv_missing_names_the_fix(scenario_repo: pathlib.Path):
    """A missing uv fails closed, with the install path named."""
    env = dict(os.environ)
    env["PATH"] = "/usr/bin:/bin"  # no fake uv, no real uv either
    env["UV_LOG"] = str(scenario_repo / "uv.log")
    result = subprocess.run(
        [str(scenario_repo / "scripts" / "run-molecule.sh"), "faketopic"],
        cwd=str(scenario_repo),
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode != 0
    assert "uv not found on PATH" in result.stderr
    assert "mise" in result.stderr, "stderr must name the install path"
    assert molecule_invocations(scenario_repo) == [], "no molecule run without uv"


def test_ephemeral_directory_is_pinned_outside_the_source(scenario_repo):
    """State must not live inside the chezmoi source (DOT-303).

    A run killed during an install left a dangling symlink in the
    in-source state dir. Chezmoi resolves the whole symlink chain while
    loading source state, so `apply` and `execute-template` failed for
    every later invocation while `managed` and `status` stayed green.
    """
    result = run_wrapper(scenario_repo, "faketopic", "converge")
    assert result.returncode == 0, result.stderr
    (record,) = molecule_records(scenario_repo)
    (value,) = record["env-ed"]

    source_root = scenario_repo / "home"
    assert not pathlib.Path(value).is_relative_to(source_root), (
        f"state must be outside the chezmoi source ({source_root}), got {value}"
    )
    # Scoped per checkout + topic + scenario, so none of them collide.
    assert value.endswith("/molecule/repo/faketopic/default"), value


def test_the_checkout_name_scopes_the_state_path(scenario_repo):
    """Two worktrees must not share run state.

    Worktrees share the git dir but not gitignored files, and the
    derived /tmp/lima-<sha1> name is a hash of this path, so a path
    without the checkout name would collide across checkouts.
    """
    result = run_wrapper(scenario_repo, "faketopic", "converge")
    assert result.returncode == 0, result.stderr
    (record,) = molecule_records(scenario_repo)
    (value,) = record["env-ed"]
    assert "/molecule/repo/" in value, f"checkout basename must scope it: {value}"


def test_named_scenario_pins_its_own_state_dir(scenario_repo, monkeypatch):
    """A named scenario keeps its own state dir, outside the source."""
    make_named_scenario(scenario_repo, "debian")
    monkeypatch.setenv("MOLECULE_SCENARIO", "debian")
    result = run_wrapper(scenario_repo, "faketopic")
    assert result.returncode == 0, result.stderr
    (record,) = molecule_records(scenario_repo)
    (value,) = record["env-ed"]
    assert value.endswith("/molecule/repo/faketopic/debian"), value
    assert not pathlib.Path(value).is_relative_to(scenario_repo / "home")


def test_legacy_in_source_state_is_reported(scenario_repo):
    """Pre-relocation state under the source is named, not ignored."""
    legacy = (
        scenario_repo
        / "home"
        / "dotfiles"
        / "apps"
        / "faketopic"
        / "molecule"
        / "default"
        / ".molecule"
    )
    legacy.mkdir(parents=True)
    result = run_wrapper(scenario_repo, "faketopic", "converge")
    assert result.returncode == 0, result.stderr
    assert "pre-relocation state" in result.stderr
    assert str(legacy) in result.stderr
    # It may belong to a run another session has in flight.
    assert legacy.is_dir(), "report it, never delete it"


def _run_with_env(scenario_repo, tmp_path, lima_tmp, state_home):
    """Run the wrapper with the report pointed at a fixture tmp root."""
    env = dict(os.environ)
    env["PATH"] = f"{scenario_repo.parent / 'fake-bin'}:{env['PATH']}"
    env["UV_LOG"] = str(scenario_repo / "uv.log")
    env["LIMA_TMP_ROOT"] = str(lima_tmp)
    env["XDG_STATE_HOME"] = str(state_home)
    return subprocess.run(
        [str(scenario_repo / "scripts" / "run-molecule.sh"), "faketopic"],
        cwd=str(scenario_repo),
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def test_a_leftover_lima_root_is_reported_before_the_run(scenario_repo, tmp_path):
    """A leftover is named, never silently removed.

    A reaper that removes quietly is the same failure with a different
    trigger, so the wrapper reports and leaves the decision to a human.
    LIMA_TMP_ROOT points the report at a fixture instead of real /tmp.
    """
    import hashlib

    lima_tmp = tmp_path / "faketmp"
    lima_tmp.mkdir()
    state_home = tmp_path / "state"
    ephemeral = f"{state_home}/molecule/repo/faketopic/default"
    digest = hashlib.sha1(ephemeral.encode()).hexdigest()
    leftover = lima_tmp / f"lima-{digest}"
    leftover.mkdir()
    (leftover / "disk").write_text("x")

    result = _run_with_env(scenario_repo, tmp_path, lima_tmp, state_home)

    assert result.returncode == 0, result.stderr
    assert "WARNING: leftover VM state" in result.stderr
    assert str(leftover) in result.stderr, "the report must name the path"
    assert "user-tmpfiles" in result.stderr, "and say what will reap it"
    # Reported, never removed, and the run still proceeded.
    assert leftover.is_dir(), "the wrapper must not delete a leftover"
    assert (leftover / "disk").exists(), "nor anything inside it"
    assert len(molecule_invocations(scenario_repo)) == 1


def test_a_clean_tmp_root_reports_nothing(scenario_repo, tmp_path):
    """No leftover must mean no warning, or it becomes noise."""
    lima_tmp = tmp_path / "emptytmp"
    lima_tmp.mkdir()
    state_home = tmp_path / "state"
    result = _run_with_env(scenario_repo, tmp_path, lima_tmp, state_home)
    assert result.returncode == 0, result.stderr
    assert "WARNING" not in result.stderr, result.stderr


def test_another_scenarios_root_is_counted_not_named(scenario_repo, tmp_path):
    """A root this scenario cannot address is counted, never removed.

    Every run uses the fixed platform name `lima-mol`, so two concurrent
    runs collide and a leftover may not be attributable at all. Say so
    rather than guessing whose it is.
    """
    lima_tmp = tmp_path / "sharedtmp"
    lima_tmp.mkdir()
    stray = lima_tmp / "lima-deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    stray.mkdir()
    state_home = tmp_path / "state"
    result = _run_with_env(scenario_repo, tmp_path, lima_tmp, state_home)
    assert result.returncode == 0, result.stderr
    assert "1 other /tmp/lima-* root(s) present" in result.stderr
    assert "not mine to remove" in result.stderr
    assert stray.is_dir(), "an unattributable root must survive the run"


def test_the_run_is_bounded_by_a_timeout(scenario_repo):
    """A hung run must fail, not run forever holding its VM.

    Molecule installs no signal handlers and tears down only on its own
    exceptions, so a hang holds its VM indefinitely (DOT-309). The bound
    is asserted on the exec line, where it actually applies: the fake uv
    logs its own argv and cannot witness the wrapper's.
    """
    script = (scenario_repo / "scripts" / "run-molecule.sh").read_text()
    (exec_line,) = [ln for ln in script.splitlines() if ln.startswith("exec ")]
    assert "TIMEOUT_CMD" in exec_line, (
        f"the timeout must wrap the exec, not sit beside it: {exec_line}"
    )
    assert "timeout --signal=TERM" in script


def test_login_is_not_bounded(scenario_repo):
    """`login` is a human at a tty; a timeout would end it."""
    script = (scenario_repo / "scripts" / "run-molecule.sh").read_text()
    assert 'if [[ "$VERB" != "login" ]]' in script
    result = run_wrapper(scenario_repo, "faketopic", "login")
    assert result.returncode == 0, result.stderr


def test_the_wrapper_never_reaps():
    """Report, never remove (DOT-309, and the permission limit).

    `limactl delete` asks in the autonomous tier (PR #143), so
    unattended cleanup could not run anyway; a deletion here would be
    both unsafe and unapproved. Checked on executable lines only: the
    wrapper prints "limactl delete" as advice, and matching that would
    be the same false positive the report itself warns about.
    """
    repo = pathlib.Path(__file__).resolve().parents[2]
    script = (repo / "scripts" / "run-molecule.sh").read_text()
    executed = [
        ln
        for ln in script.splitlines()
        if ln.strip() and not ln.lstrip().startswith("#") and "printf" not in ln
    ]
    body = "\n".join(executed)
    for destructive in ("limactl delete", "limactl prune", "molecule reset"):
        assert destructive not in body, f"must not execute {destructive!r}"
    assert 'rm -rf "$LIMA_ROOT"' not in body
