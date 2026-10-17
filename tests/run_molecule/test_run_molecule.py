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
    expected = scenario_repo / "dotfiles" / "apps" / "faketopic"
    assert record["cwd"] == [str(expected)]


def test_project_directory_is_exported(scenario_repo: pathlib.Path):
    """MOLECULE_PROJECT_DIRECTORY points at dotfiles/ for roles."""
    result = run_wrapper(scenario_repo, "faketopic", "converge")
    assert result.returncode == 0, result.stderr
    (record,) = molecule_records(scenario_repo)
    assert record["env-mpd"] == [str(scenario_repo / "dotfiles")]


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
    assert str(scenario_repo / "dotfiles" / "requirements.yml") in galaxy
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


def test_ephemeral_directory_is_pinned_into_the_scenario(scenario_repo):
    """State lives in the scenario .molecule/, not a basename cache."""
    result = run_wrapper(scenario_repo, "faketopic", "converge")
    assert result.returncode == 0, result.stderr
    (record,) = molecule_records(scenario_repo)
    (value,) = record["env-ed"]
    expected = scenario_repo / "dotfiles" / "apps" / "faketopic"
    expected = expected / "molecule" / "default" / ".molecule"
    assert value == str(expected), value


def test_extra_args_pass_through_to_molecule(scenario_repo: pathlib.Path):
    result = run_wrapper(scenario_repo, "faketopic", "test", "--destroy=never")
    assert result.returncode == 0, result.stderr
    (argv,) = molecule_invocations(scenario_repo)
    assert argv == [
        "run",
        "--frozen",
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
