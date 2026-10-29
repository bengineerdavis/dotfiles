"""run-role.sh must resolve the playbook relative to itself, not cwd.

AGENTS.md § Commands invokes the source `run-role.sh` through bash from
the repo root.
"""


def test_resolves_the_playbook_from_a_foreign_cwd(run_script, tmp_path):
    run, log = run_script
    foreign = tmp_path / "elsewhere"
    foreign.mkdir()
    result = run(foreign, "uv")
    assert result.returncode == 0, result.stderr
    assert log.exists(), "mise was never invoked — the playbook check failed first"
    argv = log.read_text()
    assert "ansible-playbook" in argv
    assert "apps/uv/playbook.yaml" in argv


def test_unknown_topic_fails_with_the_named_path(run_script, tmp_path):
    run, _ = run_script
    result = run(tmp_path, "no-such-topic")
    assert result.returncode != 0
    assert "no such topic playbook: apps/no-such-topic/playbook.yaml" in (
        result.stdout + result.stderr
    )


def test_second_argument_becomes_the_tags_flag(run_script, tmp_path):
    run, log = run_script
    result = run(tmp_path, "uv", "install")
    assert result.returncode == 0, result.stderr
    argv = log.read_text()
    assert "--tags" in argv
    assert "install" in argv
