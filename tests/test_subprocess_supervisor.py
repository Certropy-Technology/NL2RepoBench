from __future__ import annotations

import base64
import io
import json
import os
import signal
import sys
import time
from pathlib import Path
from types import SimpleNamespace

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
def test_candidate_process_changes_to_validated_cwd_and_closes_inherited_fds(
    tmp_path: Path,
) -> None:
    policy = _policy(tmp_path, environment=frozenset({"CHECK_FD"}))
    script = policy.staging_root / "bin/check-boundary"
    script.write_text(
        "#!/bin/sh\n"
        "test \"$PWD\" = \""
        + str(policy.staging_root / "write")
        + "\" || exit 11\n"
        "test -e \"/proc/self/fd/$CHECK_FD\" && exit 12\n"
        "exit 0\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    inherited = os.open(script, os.O_RDONLY)
    os.set_inheritable(inherited, True)
    try:
        result = run_candidate_process(
            CandidateCommand(
                (str(script),),
                "write",
                (("CHECK_FD", str(inherited)),),
            ),
            SubprocessLimits(timeout_sec=3, cpu_sec=3, max_output_bytes=1024),
            policy,
            request_id="4" * 32,
        )
    finally:
        os.close(inherited)
    assert result.returncode == 0
    assert result.cleanup_complete


def test_executable_root_rejects_symlink_and_candidate_writable_tree(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    link = policy.staging_root / "bin/link"
    link.symlink_to(policy.staging_root / "bin/true")
    with pytest.raises(ProcessContractError, match="symlink"):
        run_candidate_process(
            CandidateCommand((str(policy.staging_root / "bin/true"),), "."),
            SubprocessLimits(timeout_sec=1, cpu_sec=1),
            policy,
            request_id="5" * 32,
        )
    link.unlink()
    policy.allowed_executable_roots[0].chmod(0o777)
    with pytest.raises(ProcessContractError, match="writable"):
        run_candidate_process(
            CandidateCommand((str(policy.staging_root / "bin/true"),), "."),
            SubprocessLimits(timeout_sec=1, cpu_sec=1),
            policy,
            request_id="6" * 32,
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


@pytest.mark.parametrize(
    "missing", ["CapBnd", "CapInh", "CapPrm", "CapEff", "CapAmb", "NoNewPrivs"]
)
def test_child_status_requires_all_security_fields(
    monkeypatch: pytest.MonkeyPatch, missing: str
) -> None:
    fields = {
        "Uid": "10001 10001 10001 10001",
        "Gid": "10001 10001 10001 10001",
        "CapBnd": "0000000000000000",
        "CapInh": "0000000000000000",
        "CapPrm": "0000000000000000",
        "CapEff": "0000000000000000",
        "CapAmb": "0000000000000000",
        "NoNewPrivs": "1",
    }
    fields.pop(missing)

    class FakeStatus:
        def read_text(self, **kwargs: object) -> str:
            del kwargs
            return "\n".join(f"{key}: {value}" for key, value in fields.items())

    monkeypatch.setattr(subprocess_supervisor, "Path", lambda _: FakeStatus())
    with pytest.raises(OSError, match="verification"):
        subprocess_supervisor._child_status_ok(CANDIDATE_UID, CANDIDATE_GID)


def test_cleanup_kills_uid_residue_after_group_term_and_kill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    signals: list[int] = []
    monkeypatch.setattr(
        subprocess_supervisor,
        "_kill_group",
        lambda pid, signum=signal.SIGKILL: signals.append(signum),
    )
    monkeypatch.setattr(subprocess_supervisor, "terminate_uid_processes", lambda uid: None)
    monkeypatch.setattr(subprocess_supervisor, "candidate_pids", lambda uid: [])
    complete, error = subprocess_supervisor._cleanup(
        CANDIDATE_UID,
        process=SimpleNamespace(pid=123),
        deadline=time.monotonic() + 1,
    )
    assert complete
    assert error is None
    assert signals == [signal.SIGTERM, signal.SIGKILL]


def test_uid_cleanup_always_uses_sigkill(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: list[tuple[int, int]] = []
    rounds = iter([[123], [], []])
    monkeypatch.setattr(
        "nl2repobench.verification.process_cleanup.candidate_pids",
        lambda uid: next(rounds),
    )
    monkeypatch.setattr(
        "nl2repobench.verification.process_cleanup.os.kill",
        lambda pid, signum: sent.append((pid, signum)),
    )
    monkeypatch.setattr("nl2repobench.verification.process_cleanup.time.sleep", lambda _: None)
    from nl2repobench.verification.process_cleanup import terminate_uid_processes

    terminate_uid_processes(CANDIDATE_UID, attempts=2, term_attempts=1)
    assert sent == [(123, signal.SIGKILL)]


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


def test_cli_rejects_non_string_allowed_environment_names(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    request = {
        "schema_version": "1.0",
        "request_id": "1" * 32,
        "context": "call",
        "command": {"argv": ["/usr/bin/true"], "cwd": ".", "environment": []},
        "limits": {"timeout_sec": 1, "cpu_sec": 1},
        "policy": {
            "task_id": policy.task_id,
            "staging_root": str(policy.staging_root),
            "read_only_roots": [str(policy.staging_root)],
            "write_root": str(policy.write_root),
            "allowed_executable_roots": [str(policy.staging_root / "bin")],
            "allowed_environment_names": [1],
        },
        "stdin_base64": "",
    }
    with pytest.raises(ProcessContractError, match="string array"):
        candidate_process_cli._request(request)
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(
            sys,
            "stdin",
            io.TextIOWrapper(io.BytesIO((json.dumps(request) + "\n").encode())),
        )
        assert candidate_process_cli.main() == candidate_process_cli.EXIT_MALFORMED
    finally:
        monkeypatch.undo()


@pytest.mark.skipif(os.geteuid() != 0, reason="requires root to enter candidate UID")
def test_fork_setsid_escape_is_cleaned(tmp_path: Path) -> None:
    policy = _policy(tmp_path)
    script = policy.staging_root / "bin/fork-setsid"
    script.write_text(
        "#!/usr/bin/python3\n"
        "import os\n"
        "pid = os.fork()\n"
        "if pid == 0:\n"
        "    os.setsid()\n"
        "    grandchild = os.fork()\n"
        "    if grandchild == 0:\n"
        "        with open(os.devnull, 'wb') as stream:\n"
        "            os.dup2(stream.fileno(), 1)\n"
        "            os.dup2(stream.fileno(), 2)\n"
        "        os.execl('/usr/bin/sleep', 'sleep', '30')\n"
        "    os._exit(0)\n"
        "os.waitpid(pid, 0)\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    result = run_candidate_process(
        CandidateCommand((str(script),), "."),
        SubprocessLimits(timeout_sec=3, cpu_sec=3, max_output_bytes=1024),
        policy,
        request_id="7" * 32,
    )
    assert result.returncode == 0
    assert result.cleanup_complete
    assert candidate_pids(CANDIDATE_UID) == []


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
