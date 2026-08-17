from __future__ import annotations

import io
import json
import os
import shutil
import sys
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace

import pytest

from nl2repobench.verification import (
    candidate_client,
    candidate_install,
    candidate_runner,
    workspace_copy,
)
from nl2repobench.verification.candidate_client import (
    call,
    get,
    metadata_requires,
    run_console,
    run_module,
)
from nl2repobench.verification.candidate_install import tree_usage
from nl2repobench.verification.command_plan import EXPECTED_PLAN, validate_command_plan
from nl2repobench.verification.process_cleanup import terminate_uid_processes

CANDIDATE_SITE = Path("/tmp/candidate-site")


@pytest.fixture
def candidate_site(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    shutil.rmtree(CANDIDATE_SITE, ignore_errors=True)
    CANDIDATE_SITE.mkdir()
    (CANDIDATE_SITE / "demo.py").write_text(
        """VALUE = 7

def add(left, right):
    return left + right

def fail():
    raise ValueError("expected failure")

def main():
    import sys
    print("console:" + ",".join(sys.argv[1:]))
""",
        encoding="utf-8",
    )
    (CANDIDATE_SITE / "demo_cli.py").write_text(
        "import sys\nprint('module:' + ','.join(sys.argv[1:]))\n",
        encoding="utf-8",
    )
    dist_info = CANDIDATE_SITE / "demo_pkg-1.0.dist-info"
    dist_info.mkdir()
    (dist_info / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: demo-pkg\nVersion: 1.0\n",
        encoding="utf-8",
    )
    (dist_info / "entry_points.txt").write_text(
        "[console_scripts]\ndemo = demo:main\n",
        encoding="utf-8",
    )

    def direct_command(arguments: list[str]) -> list[str]:
        return [
            sys.executable,
            "-I",
            "-m",
            "nl2repobench.verification.candidate_runner",
            "--candidate-site",
            str(CANDIDATE_SITE),
            *arguments,
        ]

    monkeypatch.setattr(candidate_client, "_command", direct_command)
    monkeypatch.setattr(candidate_client, "terminate_uid_processes", lambda uid: None)
    try:
        yield CANDIDATE_SITE
    finally:
        while str(CANDIDATE_SITE) in sys.path:
            sys.path.remove(str(CANDIDATE_SITE))
        shutil.rmtree(CANDIDATE_SITE, ignore_errors=True)


def test_candidate_call_get_exception_and_metadata(candidate_site: Path) -> None:
    del candidate_site
    assert call("demo", "add", 2, 5).value == 7
    assert get("demo", "VALUE").value == 7
    failure = call("demo", "fail")
    assert failure.ok is False
    assert failure.exception_type == "builtins.ValueError"
    requirements = metadata_requires("demo-pkg")
    assert requirements.ok is True
    assert requirements.value is None


def test_candidate_module_and_console(candidate_site: Path) -> None:
    del candidate_site
    module = run_module("demo_cli", ["one", "two"])
    console = run_console("demo", ["three"])

    assert module.returncode == 0
    assert module.stdout == "module:one,two\n"
    assert console.returncode == 0
    assert console.stdout == "console:three\n"


def test_candidate_process_without_protocol_response_is_failure(candidate_site: Path) -> None:
    (candidate_site / "abrupt.py").write_text(
        "import os\ndef stop(): os._exit(0)\n",
        encoding="utf-8",
    )

    result = call("abrupt", "stop")

    assert result.ok is False
    assert result.exception_type == "CandidateProcessError"


def test_candidate_cumulative_budget_exhaustion_is_immediate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(candidate_client, "_CANDIDATE_DEADLINE", 0.0)

    result = candidate_client.run_candidate(["call"])

    assert result.returncode == 124
    assert "cumulative" in result.stderr


@pytest.mark.parametrize(
    ("request_payload", "expected"),
    [
        (
            {
                "args": [2, 3],
                "attribute": "add",
                "kwargs": {},
                "module": "demo",
                "operation": "call",
            },
            {"ok": True, "value": 5},
        ),
        (
            {
                "args": [],
                "attribute": "fail",
                "kwargs": {},
                "module": "demo",
                "operation": "call",
            },
            {"exception_type": "builtins.ValueError", "ok": False},
        ),
    ],
)
def test_candidate_runner_call_protocol(
    candidate_site: Path,
    monkeypatch: pytest.MonkeyPatch,
    request_payload: dict[str, object],
    expected: dict[str, object],
) -> None:
    candidate_runner._candidate_site(str(candidate_site))  # noqa: SLF001
    stream = io.TextIOWrapper(io.BytesIO(json.dumps(request_payload).encode()))
    monkeypatch.setattr(sys, "stdin", stream)
    emitted: dict[str, object] = {}

    def capture(payload: dict[str, object], exit_code: int = 0) -> None:
        del exit_code
        emitted.update(payload)
        raise SystemExit

    monkeypatch.setattr(candidate_runner, "_emit", capture)

    with pytest.raises(SystemExit):
        candidate_runner._call()  # noqa: SLF001

    assert all(emitted[key] == value for key, value in expected.items())


def test_candidate_runner_metadata_protocol(
    candidate_site: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    emitted: dict[str, object] = {}

    def capture(payload: dict[str, object], exit_code: int = 0) -> None:
        del exit_code
        emitted.update(payload)
        raise SystemExit

    monkeypatch.setattr(candidate_runner, "_emit", capture)

    with pytest.raises(SystemExit):
        candidate_runner._metadata_requires(candidate_site, "demo-pkg")  # noqa: SLF001

    assert emitted == {"ok": True, "value": None}


def test_candidate_runner_rejects_wrong_site(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="candidate site is unavailable"):
        candidate_runner._candidate_site(str(tmp_path))  # noqa: SLF001


def test_candidate_runner_cli_dispatches_metadata(
    candidate_site: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[Path, str]] = []
    monkeypatch.setattr(candidate_runner, "_apply_limits", lambda: None)
    monkeypatch.setattr(candidate_runner, "_candidate_site", lambda value: candidate_site)

    def metadata(site: Path, distribution: str) -> None:
        calls.append((site, distribution))
        raise SystemExit

    monkeypatch.setattr(candidate_runner, "_metadata_requires", metadata)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "candidate-runner",
            "--candidate-site",
            str(candidate_site),
            "metadata-requires",
            "demo-pkg",
        ],
    )

    with pytest.raises(SystemExit):
        candidate_runner.main()

    assert calls == [(candidate_site, "demo-pkg")]


def test_runtime_command_plan_accepts_exact_plan(tmp_path: Path) -> None:
    plan = tmp_path / "command-plan.json"
    plan.write_text(json.dumps(EXPECTED_PLAN), encoding="utf-8")

    validate_command_plan(plan)


def test_runtime_command_plan_rejects_symlink(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    target.write_text(json.dumps(EXPECTED_PLAN), encoding="utf-8")
    link = tmp_path / "link.json"
    link.symlink_to(target)

    with pytest.raises(OSError):
        validate_command_plan(link)


def test_runtime_command_plan_rejects_malformed_json(tmp_path: Path) -> None:
    plan = tmp_path / "command-plan.json"
    plan.write_text("not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid command plan JSON"):
        validate_command_plan(plan)


def test_process_cleanup_rescans_until_quiescent(monkeypatch: pytest.MonkeyPatch) -> None:
    observations = iter([[101, 102], [102], []])
    killed: list[int] = []
    monkeypatch.setattr(
        "nl2repobench.verification.process_cleanup.candidate_pids",
        lambda uid: next(observations),
    )
    monkeypatch.setattr(os, "kill", lambda pid, sig: killed.append(pid))
    monkeypatch.setattr("time.sleep", lambda seconds: None)

    terminate_uid_processes(10001, attempts=3)

    assert killed == [101, 102, 102]


def test_workspace_copy_accepts_bounded_regular_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "module.py").write_text("value = 1\n", encoding="utf-8")
    destination = tmp_path / "destination"
    monkeypatch.setattr(workspace_copy, "_harden_source", lambda path, directory: None)

    budget = workspace_copy.copy_workspace(source, destination)

    assert budget.entries == 1
    assert budget.total_bytes == len(b"value = 1\n")
    assert (destination / "module.py").read_text() == "value = 1\n"


def test_workspace_copy_rejects_special_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    os.mkfifo(source / "pipe")
    monkeypatch.setattr(workspace_copy, "_harden_source", lambda path, directory: None)

    with pytest.raises(workspace_copy.WorkspaceRejected, match="not a regular file"):
        workspace_copy.copy_workspace(source, tmp_path / "destination")


def test_candidate_tree_usage_is_bounded_summary(tmp_path: Path) -> None:
    root = tmp_path / "candidate"
    nested = root / "nested"
    nested.mkdir(parents=True)
    (root / "one.txt").write_bytes(b"one")
    (nested / "two.txt").write_bytes(b"two")

    entries, total_bytes = tree_usage((root,))

    assert entries == 3
    assert total_bytes == 6


@pytest.mark.parametrize(
    ("outcome", "expected_exit"),
    [("success", None), ("timeout", candidate_install.CANDIDATE_FAILURE_EXIT)],
)
def test_candidate_install_cli_writes_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    outcome: str,
    expected_exit: int | None,
) -> None:
    status = tmp_path / "status.json"
    result = {"entries": 1, "outcome": outcome, "returncode": 0, "total_bytes": 10}
    monkeypatch.setattr(candidate_install, "install_candidate", lambda *args: result)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "candidate-install",
            "--source",
            str(tmp_path / "source"),
            "--target",
            str(tmp_path / "target"),
            "--status",
            str(status),
        ],
    )

    if expected_exit is None:
        candidate_install.main()
    else:
        with pytest.raises(SystemExit) as raised:
            candidate_install.main()
        assert raised.value.code == expected_exit
    assert json.loads(status.read_text()) == result


def test_candidate_install_cli_records_internal_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    status = tmp_path / "status.json"

    def fail(*args: object) -> dict[str, object]:
        raise OSError("supervisor failed")

    monkeypatch.setattr(candidate_install, "install_candidate", fail)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "candidate-install",
            "--source",
            str(tmp_path / "source"),
            "--target",
            str(tmp_path / "target"),
            "--status",
            str(status),
        ],
    )

    with pytest.raises(SystemExit) as raised:
        candidate_install.main()

    assert raised.value.code == candidate_install.INTERNAL_ERROR_EXIT
    assert json.loads(status.read_text())["outcome"] == "internal-error"


def test_candidate_install_kills_process_group(monkeypatch: pytest.MonkeyPatch) -> None:
    killed: list[tuple[int, int]] = []
    monkeypatch.setattr(os, "killpg", lambda pid, sig: killed.append((pid, sig)))

    candidate_install._kill_group(SimpleNamespace(pid=123))  # type: ignore[arg-type]  # noqa: SLF001

    assert killed == [(123, candidate_install.signal.SIGKILL)]
