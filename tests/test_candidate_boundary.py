from __future__ import annotations

import base64
import io
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

from nl2repobench.verification import (
    candidate_client,
    candidate_install,
    candidate_runner,
    workspace_copy,
)
from nl2repobench.verification.candidate_client import (
    call,
    call_method,
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

class Value:
    def __init__(self, value):
        self.value = value

    def add(self, amount):
        return self.value + amount

    def same(self, other):
        return self.value == other.value

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

    def fake_invoke(request_id: str, encoded: bytes, timeout_sec: float):
        del timeout_sec
        envelope = json.loads(encoded)
        command = envelope["command"]["argv"]
        arguments = command[command.index("--candidate-site") + 2 :]
        operation = arguments[0]
        if operation == "call":
            request = json.loads(base64.b64decode(envelope["stdin_base64"]))
            if request["attribute"] == "stop":
                return candidate_client._TransportResult(  # noqa: SLF001
                    candidate_client.CandidateProcessResult(0, "", "")
                )
            if request["operation"] == "call" and request["attribute"] == "add":
                payload = {"ok": True, "value": sum(request["args"])}
            elif request["operation"] == "call" and request["attribute"] == "fail":
                payload = {
                    "exception_type": "builtins.ValueError",
                    "exception_message": "expected failure",
                    "ok": False,
                }
            elif request["operation"] == "get":
                payload = {"ok": True, "value": 7}
            elif request["operation"] == "call_method":
                if request["member"] == "same":
                    value = True
                else:
                    value = 3 + request["args"][0] if request["invoke"] else 3
                payload = {"ok": True, "value": value}
            else:
                payload = {"ok": False}
            output = candidate_runner.RESULT_PREFIX + json.dumps(payload) + "\n"
        elif operation == "module":
            output = "module:" + ",".join(arguments[2:]) + "\n"
        elif operation == "console":
            output = "console:" + ",".join(arguments[2:]) + "\n"
        elif operation == "metadata-requires":
            output = candidate_runner.RESULT_PREFIX + '{"ok":true,"value":null}\n'
        else:
            output = ""
        return candidate_client._TransportResult(  # noqa: SLF001
            candidate_client.CandidateProcessResult(0, output, "")
        )

    monkeypatch.setattr(candidate_client, "_invoke_cli", fake_invoke)
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


def test_candidate_call_method_and_property(candidate_site: Path) -> None:
    del candidate_site
    method = call_method("demo", "Value", [3], "add", 4)
    prop = call_method("demo", "Value", [3], "value", invoke=False)
    nested = call_method(
        "demo",
        "Value",
        [3],
        "same",
        {
            "__nl2repo_construct__": {
                "args": [3],
                "attribute": "Value",
                "kwargs": {},
                "module": "demo",
            }
        },
    )
    assert method.ok is True
    assert method.value == 7
    assert prop.ok is True
    assert prop.value == 3
    assert nested.ok is True
    assert nested.value is True


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


def test_candidate_runner_method_protocol(
    candidate_site: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate_runner._candidate_site(str(candidate_site))  # noqa: SLF001
    request = {
        "args": [2],
        "attribute": "Value",
        "constructor_args": [3],
        "constructor_kwargs": {},
        "invoke": True,
        "kwargs": {},
        "member": "add",
        "module": "demo",
        "operation": "call_method",
    }
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(json.dumps(request).encode())))
    emitted: dict[str, object] = {}

    def capture(payload: dict[str, object], exit_code: int = 0) -> None:
        del exit_code
        emitted.update(payload)
        raise SystemExit

    monkeypatch.setattr(candidate_runner, "_emit", capture)
    with pytest.raises(SystemExit):
        candidate_runner._call()  # noqa: SLF001
    assert emitted == {"ok": True, "value": 5}


def test_candidate_runner_script_protocol(monkeypatch: pytest.MonkeyPatch) -> None:
    stream = io.TextIOWrapper(
        io.BytesIO(json.dumps({"source": 'result = {"answer": 42}'}).encode())
    )
    monkeypatch.setattr(sys, "stdin", stream)
    emitted: dict[str, object] = {}

    def capture(payload: dict[str, object], exit_code: int = 0) -> None:
        del exit_code
        emitted.update(payload)
        raise SystemExit

    monkeypatch.setattr(candidate_runner, "_emit", capture)
    with pytest.raises(SystemExit):
        candidate_runner._script()  # noqa: SLF001
    assert emitted == {"ok": True, "value": {"answer": 42}}


def test_candidate_runner_rejects_wrong_site(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="candidate site is unavailable"):
        candidate_runner._candidate_site(str(tmp_path))  # noqa: SLF001


def test_candidate_runner_json_default_materializes_iterators() -> None:
    assert candidate_runner._json_default(iter([(1, 2), (2, 3)])) == [  # noqa: SLF001
        (1, 2),
        (2, 3),
    ]


def test_candidate_runner_json_default_uses_repr_for_objects() -> None:
    class Result:
        def __repr__(self) -> str:
            return "Result(observed)"

    assert candidate_runner._json_default(Result()) == "Result(observed)"  # noqa: SLF001


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


def _cli_response(
    request_id: str = "a" * 32,
    *,
    returncode: int = 0,
    cleanup_complete: bool = True,
    stdout: bytes = b"",
    stderr: bytes = b"",
    timed_out: bool = False,
    output_limit_exceeded: bool = False,
) -> bytes:
    return json.dumps(
        {
            "cleanup_complete": cleanup_complete,
            "output_limit_exceeded": output_limit_exceeded,
            "request_id": request_id,
            "returncode": returncode,
            "schema_version": "1.0",
            "stderr_base64": base64.b64encode(stderr).decode("ascii"),
            "stdout_base64": base64.b64encode(stdout).decode("ascii"),
            "timed_out": timed_out,
        },
        separators=(",", ":"),
    ).encode()


def test_candidate_cli_transport_success_and_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = candidate_client.CandidateProcessResult(0, "out", "err")
    monkeypatch.setattr(
        candidate_client.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0], 0, _cli_response(stdout=b"out", stderr=b"err"), b""
        ),
    )
    result = candidate_client._invoke_cli("a" * 32, b"request", 1)  # noqa: SLF001
    assert result.process == expected
    monkeypatch.setattr(
        candidate_client.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0], 0, _cli_response(returncode=3, stderr=b"failed"), b""
        ),
    )
    nonzero = candidate_client._invoke_cli("a" * 32, b"request", 1)  # noqa: SLF001
    assert nonzero.process.returncode == 3
    assert nonzero.process.stderr == "failed"


def test_candidate_cli_transport_rejects_timeout_and_exit_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 1)

    monkeypatch.setattr(candidate_client.subprocess, "run", timeout)
    timed = candidate_client._invoke_cli("a" * 32, b"request", 1)  # noqa: SLF001
    assert timed.process.returncode == 124
    assert timed.timed_out is True
    for exit_code in (64, 70, 75):
        monkeypatch.setattr(
            candidate_client.subprocess,
            "run",
            lambda *args, code=exit_code, **kwargs: subprocess.CompletedProcess(
                args[0], code, b"", b"bad transport"
            ),
        )
        result = candidate_client._invoke_cli("a" * 32, b"request", 1)  # noqa: SLF001
        assert result.process.returncode == exit_code
        assert result.process.stderr == "bad transport"


@pytest.mark.parametrize(
    "response",
    [
        b"not-json",
        _cli_response(request_id="b" * 32),
        _cli_response(cleanup_complete=False),
    ],
    ids=["malformed", "request-id-mismatch", "cleanup-failure"],
)
def test_candidate_cli_transport_rejects_malformed_result(
    monkeypatch: pytest.MonkeyPatch, response: bytes
) -> None:
    monkeypatch.setattr(
        candidate_client.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, response, b""),
    )
    result = candidate_client._invoke_cli("a" * 32, b"request", 1)  # noqa: SLF001
    assert result.process.returncode == 70
    assert "invalid candidate CLI result" in result.process.stderr


def test_candidate_cli_transport_rejects_result_flood(monkeypatch: pytest.MonkeyPatch) -> None:
    flood = b"x" * (20 * 1024 * 1024 + 1)
    monkeypatch.setattr(
        candidate_client.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, flood, b""),
    )
    result = candidate_client._invoke_cli("a" * 32, b"request", 1)  # noqa: SLF001
    assert result.process.returncode == 70
    assert result.output_limit_exceeded is True


def test_candidate_call_maps_transport_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        candidate_client,
        "_invoke_cli",
        lambda *args, **kwargs: candidate_client._TransportResult(  # noqa: SLF001
            candidate_client.CandidateProcessResult(75, "", "cleanup failed")
        ),
    )
    result = candidate_client.call("demo", "add", 1, 2)
    assert result.ok is False
    assert result.exception_type == "CandidateProcessError"
    assert "cleanup failed" in (result.exception_message or "")


@pytest.mark.parametrize(
    ("returncode", "expected_outcome"),
    [
        (64, "internal-error"),
        (70, "internal-error"),
        (75, "internal-error"),
        (2, "candidate-failure"),
    ],
    ids=["malformed-transport", "verifier-internal", "cleanup-failure", "candidate"],
)
def test_candidate_install_preserves_transport_and_candidate_mapping(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    returncode: int,
    expected_outcome: str,
) -> None:
    source = tmp_path / "source"
    source.write_bytes(b"source")
    target = tmp_path / "target"
    monkeypatch.setattr(
        candidate_install,
        "tree_usage",
        lambda paths: (0, 0),
    )
    monkeypatch.setattr(
        "nl2repobench.verification.candidate_client._run_cli_request",
        lambda *args, **kwargs: candidate_client._TransportResult(  # noqa: SLF001
            candidate_client.CandidateProcessResult(returncode, "", "transport or pip failure")
        ),
    )
    result = candidate_install.install_candidate(source, target, 1)
    assert result["outcome"] == expected_outcome
    assert result["returncode"] == returncode


def test_python_candidate_runtime_has_no_direct_spawn_or_address_space_limits() -> None:
    root = Path(__file__).parents[1] / "src/nl2repobench/verification"
    owned = "\n".join(
        (root / name).read_text(encoding="utf-8")
        for name in ("candidate_client.py", "candidate_install.py", "candidate_runner.py")
    )
    for forbidden in (
        "RLIMIT_AS",
        "address-space",
        "prlimit",
        "subprocess.Popen",
        "runuser",
        "killpg",
        "preexec_fn",
        "terminate_uid_processes",
    ):
        assert forbidden not in owned


def test_candidate_build_environment_allows_only_safe_shell_names() -> None:
    assert candidate_install._parse_build_environment(("BUILD_VERSION=0.0.0",)) == (  # noqa: SLF001
        "BUILD_VERSION=0.0.0",
    )
    with pytest.raises(ValueError, match="cannot override PATH"):
        candidate_install._parse_build_environment(("PATH=/unsafe",))  # noqa: SLF001
    with pytest.raises(ValueError, match="invalid candidate build environment"):
        candidate_install._parse_build_environment(("lowercase=value",))  # noqa: SLF001


@pytest.mark.parametrize(
    ("outcome", "expected_exit"),
    [
        ("success", None),
        ("timeout", candidate_install.CANDIDATE_FAILURE_EXIT),
        ("internal-error", candidate_install.INTERNAL_ERROR_EXIT),
    ],
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
