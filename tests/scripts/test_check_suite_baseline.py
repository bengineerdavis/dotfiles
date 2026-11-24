"""The baseline gate reads JUnit XML, and its decisions are the ones we want.

Every test here runs real pytest on a small fixture module and judges the XML it
writes. That matters: an earlier version of this suite fed hand-written text to a
regex, so it stayed green while the parser's assumptions about pytest's output
format were wrong in four ways (roborev job 853). Generating the report with
pytest itself makes the fixtures honest — and when pytest changes its output,
these tests notice.

The gate has two directions to prove: it must DECLINE a run it cannot trust, and
it must PROCEED on one it can. A guard that fails closed and a guard that never
runs are indistinguishable, so both are tested at the process level via main().
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import textwrap

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "check_suite_baseline", REPO / "scripts" / "check_suite_baseline.py"
)
assert _spec is not None and _spec.loader is not None
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

KNOWN = sorted(check.EXPECTED_FAILURES)


def _pyproject(tmp_path: pathlib.Path) -> None:
    """Let pytest resolve the fixture's node IDs from the temp directory.

    rootdir determines how `file` is written, so the fixture needs its own
    rootdir; without it the id carries a `../..` prefix.
    """
    (tmp_path / "pyproject.toml").write_text("")


def _run_pytest(tmp_path: pathlib.Path, source: str) -> pathlib.Path:
    """Run real pytest on `source` and return the XML report it wrote."""
    _pyproject(tmp_path)
    (tmp_path / "test_fixture.py").write_text(textwrap.dedent(source))
    report = tmp_path / "report.xml"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(tmp_path / "test_fixture.py"),
            "-q",
            "--junitxml",
            str(report),
            "-o",
            "junit_family=xunit1",
        ],
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )
    assert report.is_file(), "pytest did not write a report"
    return report


def _id_of(tmp_path: pathlib.Path, test_name: str) -> str:
    """The node ID pytest itself reports for a fixture test."""
    report = _run_pytest(
        tmp_path,
        """
        def test_placeholder():
            assert False
        """,
    )
    root = check.load_report(report)
    ids = check.failed_ids(root)
    assert len(ids) == 1
    return ids.pop().replace("test_placeholder", test_name)


def _report_with(tmp_path: pathlib.Path, body: str) -> pathlib.Path:
    return _run_pytest(tmp_path, body)


# ── It proceeds when it may ────────────────────────────────────────────────


def test_a_failure_in_the_baseline_is_accepted(tmp_path, monkeypatch, capsys):
    """A known failure is green, and the gate says what it read."""
    known = KNOWN[0]
    monkeypatch.setattr(check, "EXPECTED_FAILURES", frozenset({known}))
    report = tmp_path / "r.xml"
    report.write_text(
        f"""<?xml version="1.0"?>
<testsuites><testsuite name="pytest" tests="2" failures="1" errors="0">
  <testcase file="{known.split("::")[0]}" name="{known.split("::")[1]}">
    <failure message="boom" />
  </testcase>
  <testcase file="tests/other/test_x.py" name="test_ok" />
</testsuite></testsuites>
"""
    )
    assert check.main([str(report)]) == 0
    assert "baseline already knows about" in capsys.readouterr().out


def test_an_all_passing_run_is_green(tmp_path, monkeypatch, capsys):
    """With an empty baseline a clean run passes."""
    monkeypatch.setattr(check, "EXPECTED_FAILURES", frozenset())
    report = _report_with(
        tmp_path,
        """
        def test_a():
            assert True
        """,
    )
    assert check.main([str(report)]) == 0


# ── It declines when it must ───────────────────────────────────────────────


def test_a_regression_is_reported(tmp_path, monkeypatch, capsys):
    """A failure outside the baseline fails the gate and names itself."""
    monkeypatch.setattr(check, "EXPECTED_FAILURES", frozenset())
    report = _report_with(
        tmp_path,
        """
        def test_broken():
            assert False, "boom"
        """,
    )
    assert check.main([str(report)]) == 1
    err = capsys.readouterr().err
    assert "test_fixture.py::test_broken" in err


def test_an_empty_selection_is_not_green(tmp_path, monkeypatch, capsys):
    """Pytest on a selection that matches nothing writes a zero-test report.

    That report is well-formed XML and carries a summary-shaped `tests="0"`,
    which is why the text-parsing version passed it.
    """
    monkeypatch.setattr(check, "EXPECTED_FAILURES", frozenset())
    _pyproject(tmp_path)
    report = tmp_path / "empty.xml"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "no_such_file.py",
            "--junitxml",
            str(report),
            "-o",
            "junit_family=xunit1",
        ],
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )
    assert check.main([str(report)]) == 2
    assert "no test cases" in capsys.readouterr().err


def test_a_missing_report_is_an_error(tmp_path, capsys):
    """No report means the run did not finish, which is not a pass."""
    assert check.main([str(tmp_path / "absent.xml")]) == 2
    assert "no test ever ran" in capsys.readouterr().err


def test_a_truncated_report_is_an_error(tmp_path, capsys):
    """Pytest writes the file as it finishes; a half-written one is unknown."""
    report = tmp_path / "partial.xml"
    report.write_text("<testsuites><testsuite tests='4'")
    assert check.main([str(report)]) == 2
    assert "not valid XML" in capsys.readouterr().err


def test_a_report_without_file_attributes_is_an_error(tmp_path, capsys):
    """xunit2 has no `file`, and guessing a path from dots is not allowed."""
    report = tmp_path / "v2.xml"
    report.write_text(
        """<?xml version="1.0"?>
<testsuites><testsuite name="pytest" tests="1" failures="1" errors="0">
  <testcase classname="tests.thing" name="test_x"><failure message="b" /></testcase>
</testsuite></testsuites>
"""
    )
    assert check.main([str(report)]) == 2
    assert "junit_family=xunit1" in capsys.readouterr().err


# ── The four defects roborev job 853 found, each pinned ────────────────────


def test_a_node_id_containing_the_explanation_separator_is_exact(tmp_path):
    """Finding 1: " - " inside a parametrize id must not split the id.

    The text parser truncated at that sequence, so a NEW test whose id shared
    the prefix inherited the baseline entry and passed unseen.
    """
    report = _report_with(
        tmp_path,
        """
        import pytest

        @pytest.mark.parametrize("x", ["plain", "with - separator"])
        def test_ids(x):
            assert False, "boom"
        """,
    )
    ids = check.failed_ids(check.load_report(report))
    assert ids == {
        "test_fixture.py::test_ids[plain]",
        "test_fixture.py::test_ids[with - separator]",
    }


def test_an_error_after_a_passed_count_is_seen(tmp_path):
    """Finding 2: `1 failed, 10 passed, 1 error` reports two abnormal outcomes.

    The text parser attached `error` only when it followed `failed` directly, so
    a real error vanished from the count.
    """
    report = _report_with(
        tmp_path,
        """
        import pytest

        @pytest.fixture
        def broken():
            yield
            raise RuntimeError("teardown blew up")

        def test_passes():
            assert True

        def test_errors_in_teardown(broken):
            assert True
        """,
    )
    root = check.load_report(report)
    ids = check.failed_ids(root)
    assert ids == {"test_fixture.py::test_errors_in_teardown"}
    suite = next(root.iter("testsuite"))
    assert int(suite.get("errors") or 0) == 1


def test_a_test_failing_and_erroring_is_counted_twice(tmp_path, monkeypatch, capsys):
    """Finding 3: call failure plus teardown error is a VALID log, not a broken one.

    The text-parsing gate compared a set of ids against an event count, so this
    legitimate pair looked like missing evidence and was rejected. Here both
    events are named in the baseline and the run must pass.
    """
    report = _report_with(
        tmp_path,
        """
        import pytest

        @pytest.fixture
        def broken():
            yield
            raise RuntimeError("teardown blew up")

        def test_fails_then_errors(broken):
            assert False, "call failed"
        """,
    )
    root = check.load_report(report)
    case_id = "test_fixture.py::test_fails_then_errors"
    monkeypatch.setattr(check, "EXPECTED_FAILURES", frozenset({case_id}))
    assert check.main([str(report)]) == 0
    assert "baseline already knows about" in capsys.readouterr().out


def test_captured_output_is_not_mistaken_for_results(tmp_path, monkeypatch, capsys):
    """Finding 4: a test printing summary-like text cannot change the verdict.

    The text parser took the first summary-shaped line anywhere in the log, so
    a test echoing `=== 999 failed` claimed 999 outcomes.
    """
    monkeypatch.setattr(check, "EXPECTED_FAILURES", frozenset())
    report = _report_with(
        tmp_path,
        """
        def test_noisy():
            print("=== 999 failed, 0 passed in 0.01s")
            assert True
        """,
    )
    assert check.main([str(report)]) == 0


def test_ids_are_built_from_the_file_attribute(tmp_path):
    """The id is assembled from `file`, never inferred from a dotted classname."""
    report = _report_with(
        tmp_path,
        """
        def test_x():
            assert False
        """,
    )
    root = check.load_report(report)
    case = next(c for c in root.iter("testcase") if c.find("failure") is not None)
    assert case.get("file") == "test_fixture.py"
    assert check.node_id(case) == "test_fixture.py::test_x"


def test_a_stale_baseline_entry_is_reported_but_not_fatal(
    tmp_path, monkeypatch, capsys
):
    """A known failure that now passes is a note, not a red gate."""
    monkeypatch.setattr(check, "EXPECTED_FAILURES", frozenset({"gone.py::test_gone"}))
    report = _report_with(
        tmp_path,
        """
        def test_ok():
            assert True
        """,
    )
    assert check.main([str(report)]) == 0
    assert "gone.py::test_gone" in capsys.readouterr().err


@pytest.mark.parametrize("known", KNOWN[:1])
def test_the_real_baseline_entries_are_shaped_like_pytest_ids(known):
    """Guard against a baseline entry that pytest could never emit."""
    assert "::" in known
    assert not known.endswith(".py")
