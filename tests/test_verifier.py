from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from nl2repobench.domain.canonical_models import FailureClass
from nl2repobench.verification import cli as verifier_cli
from nl2repobench.verification import network_check, pytest_plugin
from nl2repobench.verification.evaluator import EvaluationResult
from nl2repobench.verification.grader import grade_verification, write_grading_outputs
from nl2repobench.verification.integrity import hash_paths
from nl2repobench.verification.junit import JUnitError, parse_junit
from nl2repobench.verification.network_check import public_network_available
from nl2repobench.verification.taxonomy import VerificationReason


def test_network_receipt_rejects_oversized_route_table(tmp_path: Path) -> None:
    namespace = tmp_path / "namespace"
    namespace.symlink_to("net:[1]")
    route = tmp_path / "route"
    route.write_bytes(b"x" * (network_check.MAX_ROUTE_TABLE_BYTES + 1))

    with pytest.raises(ValueError, match="exceeds"):
        network_check.build_receipt(
            {"pypi.org:443": False},
            namespace_path=namespace,
            route_path=route,
        )


def test_network_check_internal_failure_exits_70(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "network.json"
    monkeypatch.setattr(network_check, "probe_public_network", lambda: {})
    monkeypatch.setattr(
        network_check,
        "build_receipt",
        lambda probes: (_ for _ in ()).throw(ValueError("receipt failed")),
    )
    monkeypatch.setattr(sys, "argv", ["network-check", "--output", str(output)])

    with pytest.raises(SystemExit) as exc:
        network_check.main()

    assert exc.value.code == 70
    assert not output.exists()


def _collection(count: int, *, errors: list[dict[str, str]] | None = None) -> bytes:
    return json.dumps(
        {
            "schema_version": "1.0",
            "collected": count,
            "nodeids": [f"test_demo.py::test_{index}" for index in range(count)],
            "collection_errors": errors or [],
        }
    ).encode()


def test_junit_classifies_each_case_once() -> None:
    counts = parse_junit(
        b"""<testsuite>
        <testcase name="pass" />
        <testcase name="fail"><failure /></testcase>
        <testcase name="error"><error /></testcase>
        <testcase name="skip"><skipped /></testcase>
        </testsuite>"""
    )

    assert counts.model_dump() | {}  # exercise strict serializability
    assert (counts.collected, counts.passed, counts.failed, counts.errors, counts.skipped) == (
        4,
        1,
        1,
        1,
        1,
    )


def test_junit_rejects_entity_expansion() -> None:
    with pytest.raises(JUnitError, match="cannot parse"):
        parse_junit(
            b'<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
            b'<testsuite><testcase name="x">&xxe;</testcase></testsuite>'
        )


def test_fixed_denominator_returns_partial_reward() -> None:
    result = grade_verification(
        expected_total=2,
        junit_data=(
            b'<testsuite><testcase name="pass" />'
            b'<testcase name="fail"><failure /></testcase></testsuite>'
        ),
        collection_data=_collection(2),
        pytest_exit_code=1,
    )

    assert result.valid is True
    assert result.reward == 0.5
    assert result.failure_reason is None
    assert isinstance(result, EvaluationResult)


def test_candidate_install_failure_is_valid_model_zero() -> None:
    result = grade_verification(
        expected_total=10,
        junit_data=None,
        collection_data=None,
        pytest_exit_code=None,
        explicit_reason=VerificationReason.CANDIDATE_INSTALLATION_FAILED,
    )

    assert result.valid is True
    assert result.reward == 0.0
    assert result.failure_class is FailureClass.MODEL


def test_missing_junit_is_invalid_verifier_result() -> None:
    result = grade_verification(
        expected_total=1,
        junit_data=None,
        collection_data=_collection(1),
        pytest_exit_code=0,
    )

    assert result.valid is False
    assert result.failure_reason is VerificationReason.REPORT_MISSING
    assert result.failure_class is FailureClass.VERIFIER


def test_collection_mismatch_is_invalid_verifier_result() -> None:
    result = grade_verification(
        expected_total=2,
        junit_data=b'<testsuite><testcase name="pass" /></testsuite>',
        collection_data=_collection(1),
        pytest_exit_code=0,
    )

    assert result.valid is False
    assert result.reward == 0.0
    assert result.failure_reason is VerificationReason.COLLECTION_MISMATCH
    assert result.failure_class is FailureClass.VERIFIER


def test_abnormal_pytest_exit_is_invalid() -> None:
    result = grade_verification(
        expected_total=1,
        junit_data=b'<testsuite><testcase name="pass" /></testsuite>',
        collection_data=_collection(1),
        pytest_exit_code=3,
    )

    assert result.valid is False
    assert result.failure_reason is VerificationReason.RUNNER_ABNORMAL_EXIT


def test_abnormal_exit_takes_precedence_over_collection_mismatch() -> None:
    result = grade_verification(
        expected_total=2,
        junit_data=b'<testsuite><testcase name="pass" /></testsuite>',
        collection_data=_collection(1),
        pytest_exit_code=3,
    )

    assert result.valid is False
    assert result.failure_reason is VerificationReason.RUNNER_ABNORMAL_EXIT


@pytest.mark.parametrize(
    ("junit", "exit_code"),
    [
        (b'<testsuite><testcase name="pass" /></testsuite>', 1),
        (
            b'<testsuite><testcase name="fail"><failure /></testcase></testsuite>',
            0,
        ),
    ],
)
def test_pytest_exit_must_match_junit_statuses(junit: bytes, exit_code: int) -> None:
    result = grade_verification(
        expected_total=1,
        junit_data=junit,
        collection_data=_collection(1),
        pytest_exit_code=exit_code,
    )

    assert result.valid is False
    assert result.failure_reason is VerificationReason.REPORT_EXIT_MISMATCH
    assert result.failure_class is FailureClass.VERIFIER


def test_grading_outputs_keep_reward_numeric(tmp_path) -> None:
    result = grade_verification(
        expected_total=1,
        junit_data=b'<testsuite><testcase name="pass" /></testsuite>',
        collection_data=_collection(1),
        pytest_exit_code=0,
    )
    write_grading_outputs(result, tmp_path)

    assert json.loads((tmp_path / "reward.json").read_text()) == {
        "reward": 1.0,
        "test_pass_rate": 1.0,
    }
    details = json.loads((tmp_path / "grading.json").read_text())
    assert details["valid"] is True
    assert details["counts"]["passed"] == 1


def test_pytest_plugin_writes_structured_collection_report(tmp_path) -> None:
    test_file = tmp_path / "test_sample.py"
    test_file.write_text(
        "def test_one(): assert True\n\ndef test_two(): assert True\n",
        encoding="utf-8",
    )
    collection = tmp_path / "collection.json"
    junit = tmp_path / "junit.xml"
    environment = os.environ.copy()
    environment["NL2REPO_COLLECTION_REPORT"] = str(collection)
    environment["PYTEST_ADDOPTS"] = "--no-cov"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "nl2repobench.verification.pytest_plugin",
            f"--junitxml={junit}",
            str(test_file),
        ],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(collection.read_text())
    assert report["collected"] == 2
    assert report["collection_errors"] == []
    assert len(report["nodeids"]) == 2


def test_pytest_plugin_hooks_write_report_in_process(tmp_path, monkeypatch) -> None:
    collection = tmp_path / "collection.json"
    monkeypatch.setenv("NL2REPO_COLLECTION_REPORT", str(collection))
    session = SimpleNamespace(items=[SimpleNamespace(nodeid="test_demo.py::test_one")])
    pytest_plugin.pytest_sessionstart(session)
    pytest_plugin.pytest_collection_finish(session)
    pytest_plugin.pytest_sessionfinish(session, 0)

    assert json.loads(collection.read_text())["nodeids"] == ["test_demo.py::test_one"]


def test_verifier_cli_writes_outputs(tmp_path, monkeypatch) -> None:
    junit = tmp_path / "junit.xml"
    collection = tmp_path / "collection.json"
    output = tmp_path / "output"
    junit.write_text('<testsuite><testcase name="pass" /></testsuite>', encoding="utf-8")
    collection.write_bytes(_collection(1))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "grade",
            "--expected",
            "1",
            "--runtime",
            "python",
            "--junit",
            str(junit),
            "--collection",
            str(collection),
            "--pytest-exit-code",
            "0",
            "--output",
            str(output),
        ],
    )

    verifier_cli.main()
    assert json.loads((output / "reward.json").read_text())["reward"] == 1.0


def test_verifier_report_reader_rejects_symlink_fifo_and_oversize(tmp_path) -> None:
    report = tmp_path / "report.json"
    report.write_bytes(b"{}")
    link = tmp_path / "report-link.json"
    link.symlink_to(report)
    fifo = tmp_path / "report.fifo"
    os.mkfifo(fifo)

    assert verifier_cli._optional_bytes(report, max_bytes=2) == b"{}"  # noqa: SLF001
    assert verifier_cli._optional_bytes(report, max_bytes=1) is None  # noqa: SLF001
    assert verifier_cli._optional_bytes(link, max_bytes=2) is None  # noqa: SLF001
    assert verifier_cli._optional_bytes(fifo, max_bytes=2) is None  # noqa: SLF001


def test_network_probe_reports_blocked_connection(monkeypatch) -> None:
    def blocked(*args, **kwargs):
        del args, kwargs
        raise OSError("blocked")

    monkeypatch.setattr("socket.create_connection", blocked)
    assert public_network_available(timeout_sec=0.01) is False


def test_integrity_hashes_content_size_and_mode(tmp_path) -> None:
    trusted = tmp_path / "trusted"
    trusted.mkdir()
    source = trusted / "source.py"
    source.write_text("value = 1\n", encoding="utf-8")
    source.chmod(0o500)

    records = hash_paths([trusted])

    assert records[str(source)]["size_bytes"] == len(b"value = 1\n")
    assert records[str(source)]["mode"] == 0o500
    assert len(str(records[str(source)]["sha256"])) == 64


def test_integrity_rejects_symlink(tmp_path) -> None:
    trusted = tmp_path / "trusted"
    trusted.mkdir()
    target = trusted / "target.py"
    target.write_text("pass\n", encoding="utf-8")
    (trusted / "link.py").symlink_to(target)

    with pytest.raises(ValueError, match="trusted tree contains symlink"):
        hash_paths([trusted])
