from __future__ import annotations

import base64
import io
import json
import os
import sys
from pathlib import Path

import pytest

from nl2repobench.verification import candidate_process_cli, subprocess_supervisor
from nl2repobench.verification.process_cleanup import candidate_pids
from nl2repobench.verification.subprocess_supervisor import (
    CANDIDATE_GID,
    CANDIDATE_UID,
    HARD_OUTPUT_BYTES,
    CandidateCommand,
    CandidateProcessPolicy,
    ProcessContractError,
    ProcessError,
    SubprocessLimits,
    run_candidate_process,
)


def _policy(tmp_path: Path, *, environment: frozenset[str] = frozenset()) -> CandidateProcessPolicy:
    for parent in (tmp_path, tmp_path.parent, tmp_path.parent.parent):
        parent.chmod(0o755)
    staging = tmp_path / "staging"
    write = staging / "write"
    executable_root = staging / "bin"
    staging.mkdir()
    write.mkdir()
    executable_root.mkdir()
    staging.chmod(0o755)
    write.chmod(0o755)
    executable_root.chmod(0o755)
    for name in ("true", "false", "printenv", "sleep", "yes"):
        target = executable_root / name
        target.write_bytes(Path("/usr/bin").joinpath(name).read_bytes())
        target.chmod(0o755)
    return CandidateProcessPolicy(
        task_id="test-task",
        staging_root=staging,
        read_only_roots=(staging,),
        write_root=write,
        allowed_executable_roots=(executable_root,),
        allowed_environment_names=environment,
    )


def test_process_error_requires_matching_stage() -> None:
    with pytest.raises(ProcessContractError):
        ProcessError("spawn-failed", "cleanup", "bad")


def test_residual_result_uses_cleanup_error_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    policy = _policy(tmp_path)
    monkeypatch.setattr(
        "nl2repobench.verification.subprocess_supervisor.candidate_pids",
        lambda uid: [123] if uid == CANDIDATE_UID else [],
    )
    result = run_candidate_process(
        CandidateCommand((str(policy.staging_root / "bin/true"),), "."),
        SubprocessLimits(timeout_sec=1, cpu_sec=1),
        policy,
        request_id="0" * 32,
    )
    assert result.spawn_error is None
    assert result.cleanup_error is not None
    assert result.cleanup_error.code == "cleanup-residue"


def test_limits_are_lower_only() -> None:
    limits = SubprocessLimits(
        timeout_sec=1,
        cpu_sec=1,
        max_stdin_bytes=32,
        max_output_bytes=64,
        max_file_bytes=1024,
        max_open_files=32,
        max_processes=4,
    )
    assert limits.uid == CANDIDATE_UID
    assert limits.gid == CANDIDATE_GID
    with pytest.raises(ProcessContractError):
        SubprocessLimits(max_output_bytes=HARD_OUTPUT_BYTES + 1)


def test_policy_requires_literal_security_flags(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    with pytest.raises(ProcessContractError):
        CandidateProcessPolicy(
            task_id=policy.task_id,
            staging_root=policy.staging_root,
            read_only_roots=policy.read_only_roots,
            write_root=policy.write_root,
            allowed_executable_roots=policy.allowed_executable_roots,
            allowed_environment_names=frozenset(),
            require_no_new_privs=1,
        )


def test_hardlinks_are_rejected_before_spawn(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    hardlink = policy.staging_root / "hardlink"
    hardlink.hardlink_to(policy.staging_root / "bin/true")
    with pytest.raises(ProcessContractError, match="hardlink"):
        run_candidate_process(
            CandidateCommand((str(policy.staging_root / "bin/true"),), "."),
            SubprocessLimits(timeout_sec=1, cpu_sec=1),
            policy,
            request_id="1" * 32,
        )


@pytest.mark.skipif(os.geteuid() != 0, reason="requires root to enter candidate UID")
def test_candidate_process_success_and_nonzero(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    limits = SubprocessLimits(timeout_sec=3, cpu_sec=3, max_output_bytes=1024)
    success = run_candidate_process(
        CandidateCommand((str(policy.staging_root / "bin/true"),), "."),
        limits,
        policy,
        request_id="a" * 32,
    )
    assert success.returncode == 0
    assert success.cleanup_complete
    failure = run_candidate_process(
        CandidateCommand((str(policy.staging_root / "bin/false"),), "."),
        limits,
        policy,
        request_id="b" * 32,
    )
    assert failure.returncode != 0
    assert failure.spawn_error is None
    assert failure.cleanup_complete


@pytest.mark.skipif(os.geteuid() != 0, reason="requires root to enter candidate UID")
def test_candidate_process_passes_bounded_stdin_and_environment(tmp_path: Path) -> None:
    policy = _policy(tmp_path, environment=frozenset({"TEST_VALUE"}))
    result = run_candidate_process(
        CandidateCommand(
            (str(policy.staging_root / "bin/printenv"), "TEST_VALUE"), ".", (("TEST_VALUE", "ok"),)
        ),
        SubprocessLimits(timeout_sec=3, cpu_sec=3, max_output_bytes=1024),
        policy,
        request_id="c" * 32,
    )
    assert result.stdout == b"ok\n"
    assert result.cleanup_complete


@pytest.mark.skipif(os.geteuid() != 0, reason="requires root to enter candidate UID")
def test_candidate_process_timeout_and_output_limit(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    timeout = run_candidate_process(
        CandidateCommand((str(policy.staging_root / "bin/sleep"), "10"), "."),
        SubprocessLimits(timeout_sec=0.1, cpu_sec=1, max_output_bytes=1024),
        policy,
        request_id="d" * 32,
    )
    assert timeout.timed_out
    assert timeout.returncode == 124
    assert timeout.cleanup_complete
    flood = run_candidate_process(
        CandidateCommand((str(policy.staging_root / "bin/yes"), "x"), "."),
        SubprocessLimits(timeout_sec=3, cpu_sec=3, max_output_bytes=1024),
        policy,
        request_id="e" * 32,
    )
    assert flood.output_limit_exceeded
    assert flood.returncode == 125
    assert len(flood.stdout) + len(flood.stderr) <= 1024
    assert flood.cleanup_complete


@pytest.mark.skipif(os.geteuid() != 0, reason="requires root to enter candidate UID")
def test_exec_failure_is_distinct_from_spawn_failure(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    script = policy.staging_root / "bin/bad-script"
    script.write_text("#!/missing/interpreter\n", encoding="utf-8")
    script.chmod(0o755)
    result = run_candidate_process(
        CandidateCommand((str(script),), "."),
        SubprocessLimits(timeout_sec=1, cpu_sec=1),
        policy,
        request_id="2" * 32,
    )
    assert result.returncode == 127
    assert result.spawn_error is not None
    assert result.spawn_error.code == "exec-failed"
    assert result.spawn_error.stage == "exec"


@pytest.mark.skipif(os.geteuid() != 0, reason="requires root to enter candidate UID")
def test_capability_drop_eperm_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    policy = _policy(tmp_path)
    original = subprocess_supervisor._prctl

    def fail_capability(option: int, *args: int) -> None:
        if option == subprocess_supervisor._PR_CAPBSET_DROP:
            raise OSError(1, "operation not permitted")
        original(option, *args)

    monkeypatch.setattr(subprocess_supervisor, "_prctl", fail_capability)
    result = run_candidate_process(
        CandidateCommand((str(policy.staging_root / "bin/true"),), "."),
        SubprocessLimits(timeout_sec=1, cpu_sec=1),
        policy,
        request_id="3" * 32,
    )
    assert result.returncode == 127
    assert result.spawn_error is not None
    assert result.spawn_error.code == "preexec-failed"
    assert result.cleanup_complete


def test_cli_rejects_duplicate_and_malformed_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    duplicate = b'{"schema_version":"1.0","schema_version":"1.0"}'
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(duplicate)))
    assert candidate_process_cli.main() == candidate_process_cli.EXIT_MALFORMED

    malformed = json.dumps({"schema_version": "1.0", "request_id": "z" * 32}).encode()
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(malformed)))
    assert candidate_process_cli.main() == candidate_process_cli.EXIT_MALFORMED


def test_cli_request_decodes_canonical_stdin(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    request = {
        "schema_version": "1.0",
        "request_id": "f" * 32,
        "context": "call",
        "command": {"argv": ["/usr/bin/true"], "cwd": ".", "environment": []},
        "limits": {"timeout_sec": 1, "cpu_sec": 1},
        "policy": {
            "task_id": policy.task_id,
            "staging_root": str(policy.staging_root),
            "read_only_roots": [str(policy.staging_root)],
            "write_root": str(policy.write_root),
            "allowed_executable_roots": [str(policy.staging_root / "bin")],
            "allowed_environment_names": [],
        },
        "stdin_base64": base64.b64encode(b"").decode(),
    }
    request_id, command, limits, parsed_policy, data = candidate_process_cli._request(request)
    assert request_id == "f" * 32
    assert command.argv == ("/usr/bin/true",)
    assert limits.timeout_sec == 1
    assert parsed_policy.task_id == policy.task_id
    assert data == b""


def test_cli_maps_internal_oserror_to_exit_70(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_request(value: object) -> object:
        del value
        raise OSError("internal")

    monkeypatch.setattr(candidate_process_cli, "_request", fail_request)
    monkeypatch.setattr(
        sys,
        "stdin",
        io.TextIOWrapper(io.BytesIO(b'{"schema_version":"1.0"}')),
    )
    assert candidate_process_cli.main() == candidate_process_cli.EXIT_INTERNAL


def test_candidate_pids_matches_any_uid_tuple(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakePath:
        def __init__(self, value: str) -> None:
            self.value = value
            self.parent = self
            self.name = "123"

        def read_text(self, **kwargs: object) -> str:
            del kwargs
            return "Name:\ttest\nUid:\t1 2 10001 4\n"

        def glob(self, pattern: str) -> list[FakePath]:
            del pattern
            return [self]

    class FakePathFactory:
        def __new__(cls, value: str) -> FakePath:
            del cls
            return FakePath(value)

    monkeypatch.setattr("nl2repobench.verification.process_cleanup.Path", FakePathFactory)
    assert candidate_pids(10001) == [123]
