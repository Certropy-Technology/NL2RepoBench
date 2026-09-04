from __future__ import annotations

from pathlib import Path

import pytest

from nl2repobench.harbor.java_compiler import JavaHarborCompileError, JavaHarborCompiler
from nl2repobench.verification import subprocess_supervisor
from nl2repobench.verification.subprocess_supervisor import (
    ProcessLimits,
    apply_process_limits,
    run_supervised_process,
)


def _limits(timeout: float = 1.0) -> ProcessLimits:
    return ProcessLimits(
        timeout_sec=timeout,
        max_output_bytes=1024,
        address_space_bytes=512 * 1024 * 1024,
    )


def test_shared_supervisor_runs_argv_and_captures_output(tmp_path: Path) -> None:
    result = run_supervised_process(
        ["/bin/sh", "-c", "printf shared"],
        cwd=tmp_path,
        uid=0,
        limits=_limits(),
        environment={"PATH": "/usr/bin:/bin"},
    )

    assert result.return_code == 0
    assert result.stdout == "shared"
    assert result.stderr == ""
    assert result.timed_out is False


@pytest.mark.parametrize(
    "command,limits,error",
    [
        ([], _limits(), "non-empty argv"),
        (["/bin/true"], ProcessLimits(0, 1), "finite and positive"),
        (["/bin/true"], ProcessLimits(1, 0), "output limit"),
        (["/bin/true"], ProcessLimits(1, 1, address_space_bytes=0), "address space"),
        (["/bin/true"], ProcessLimits(1, 1, max_open_files=0), "count and file"),
    ],
)
def test_shared_supervisor_rejects_invalid_limits(
    tmp_path: Path, command: list[str], limits: ProcessLimits, error: str
) -> None:
    with pytest.raises(ValueError, match=error):
        run_supervised_process(
            command,
            cwd=tmp_path,
            uid=0,
            limits=limits,
            environment={"PATH": "/usr/bin:/bin"},
        )


def test_shared_supervisor_reports_spawn_signal_and_truncation(tmp_path: Path) -> None:
    missing = run_supervised_process(
        ["/missing-command"],
        cwd=tmp_path,
        uid=0,
        limits=_limits(),
        environment={"PATH": "/usr/bin:/bin"},
    )
    assert missing.spawn_error is not None
    signaled = run_supervised_process(
        ["/bin/sh", "-c", "kill -TERM $$"],
        cwd=tmp_path,
        uid=0,
        limits=_limits(),
        environment={"PATH": "/usr/bin:/bin"},
    )
    assert signaled.signal == 15
    output = run_supervised_process(
        ["/bin/sh", "-c", "printf 123456; printf abcdef >&2"],
        cwd=tmp_path,
        uid=0,
        limits=ProcessLimits(timeout_sec=1, max_output_bytes=3),
        environment={"PATH": "/usr/bin:/bin"},
        stdin_data=b"",
    )
    assert output.stdout == "123"
    assert output.stderr == "abc"
    assert output.stdout_truncated and output.stderr_truncated


def test_java_locked_file_rejects_escape_symlink_and_missing(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.write_text("value", encoding="utf-8")
    inside = root / "inside"
    inside.write_text("value", encoding="utf-8")
    (root / "linked").symlink_to(inside)

    with pytest.raises(JavaHarborCompileError, match="relative and confined"):
        JavaHarborCompiler._locked_file(root, "../outside", "lock")  # noqa: SLF001
    with pytest.raises(JavaHarborCompileError, match="symlink"):
        JavaHarborCompiler._locked_file(root, "linked", "lock")  # noqa: SLF001
    with pytest.raises(JavaHarborCompileError, match="missing"):
        JavaHarborCompiler._locked_file(root, "missing", "lock")  # noqa: SLF001


def test_shared_process_limits_apply_rlimits_and_privilege_drop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rlimits: list[tuple[int, tuple[int, int]]] = []
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(
        subprocess_supervisor.resource,
        "setrlimit",
        lambda kind, value: rlimits.append((kind, value)),
    )
    monkeypatch.setattr(subprocess_supervisor.os, "geteuid", lambda: 0)
    monkeypatch.setattr(
        subprocess_supervisor.pwd,
        "getpwuid",
        lambda uid: type("Account", (), {"pw_gid": uid + 1})(),
    )
    monkeypatch.setattr(
        subprocess_supervisor.os, "setgroups", lambda groups: calls.append(("groups", groups))
    )
    monkeypatch.setattr(
        subprocess_supervisor.os, "setgid", lambda gid: calls.append(("gid", gid))
    )
    monkeypatch.setattr(
        subprocess_supervisor.os, "setuid", lambda uid: calls.append(("uid", uid))
    )

    apply_process_limits(
        10001,
        ProcessLimits(
            timeout_sec=1.2,
            max_output_bytes=1024,
            address_space_bytes=4096,
            max_open_files=64,
            max_processes=32,
        ),
    )

    assert len(rlimits) == 6
    assert calls == [("groups", []), ("gid", 10002), ("uid", 10001)]


def test_shared_supervisor_writes_stdin_and_times_out(tmp_path: Path) -> None:
    result = run_supervised_process(
        ["/bin/sh", "-c", "read value; printf '%s' \"$value\""],
        cwd=tmp_path,
        uid=0,
        limits=_limits(),
        environment={"PATH": "/usr/bin:/bin"},
        stdin_data=b"request\n",
    )

    assert result.return_code == 0
    assert result.stdout == "request"
    assert result.timed_out is False

    timeout_result = run_supervised_process(
        ["/bin/sh", "-c", "sleep 10"],
        cwd=tmp_path,
        uid=0,
        limits=_limits(0.1),
        environment={"PATH": "/usr/bin:/bin"},
    )
    assert timeout_result.timed_out is True
    assert timeout_result.return_code is None


def test_shared_supervisor_closes_pipes_and_cleans_escaped_candidate(
    tmp_path: Path,
) -> None:
    if __import__("os").geteuid() != 0:
        return
    result = run_supervised_process(
        [
            "/bin/sh",
            "-c",
            "setsid sh -c 'sleep 30' >/dev/null 2>&1 & exit 0",
        ],
        cwd=tmp_path,
        uid=10001,
        limits=_limits(),
        environment={"PATH": "/usr/bin:/bin"},
    )

    assert result.return_code == 0
