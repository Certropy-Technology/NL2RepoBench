from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from nl2repobench.verification import candidate_process_cli
from nl2repobench.verification.candidate_process_cli import exec_candidate_process


def test_candidate_process_cli_execs_with_sanitized_environment(tmp_path: Path) -> None:
    command = [
        sys.executable,
        "-c",
        "import sys; sys.path.insert(0, 'src'); from "
        "nl2repobench.verification.candidate_process_cli import main; raise SystemExit(main())",
        "--cwd",
        str(tmp_path),
        "--uid",
        str(os.getuid()),
        "--timeout-sec",
        "2",
        "--",
        "/usr/bin/env",
    ]
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "API_KEY": "must-not-leak"},
    )

    assert "API_KEY" not in result.stdout
    assert "HOME=/home/candidate" in result.stdout


def test_candidate_process_cli_rejects_invalid_inputs(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="non-empty argv"):
        exec_candidate_process(
            [],
            cwd=tmp_path,
            uid=os.getuid(),
            timeout_sec=1,
            address_space_bytes=1024,
        )


def test_candidate_process_exec_contract_is_sanitized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    applied: list[tuple[int, object]] = []
    executed: list[tuple[str, list[str], dict[str, str]]] = []
    monkeypatch.setenv("API_KEY", "must-not-leak")
    monkeypatch.setattr(
        candidate_process_cli,
        "apply_process_limits",
        lambda uid, limits: applied.append((uid, limits)),
    )

    def fake_exec(file: str, argv: list[str], environment: dict[str, str]) -> None:
        executed.append((file, argv, environment))
        raise OSError("exec stopped by test")

    monkeypatch.setattr(candidate_process_cli.os, "execvpe", fake_exec)
    with pytest.raises(OSError, match="exec stopped"):
        exec_candidate_process(
            ["/bin/echo", "value"],
            cwd=tmp_path,
            uid=10001,
            timeout_sec=3,
            address_space_bytes=4096,
        )

    assert applied[0][0] == 10001
    assert executed[0][0:2] == ("/bin/echo", ["/bin/echo", "value"])
    assert "API_KEY" not in executed[0][2]
    assert executed[0][2]["HOME"] == "/home/candidate"


def test_candidate_process_main_reports_setup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        candidate_process_cli,
        "exec_candidate_process",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("no exec")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "candidate-process",
            "--cwd",
            str(tmp_path),
            "--uid",
            "10001",
            "--timeout-sec",
            "1",
            "--",
            "/bin/true",
        ],
    )

    assert candidate_process_cli.main() == 127
    assert "candidate process setup failed: no exec" in capsys.readouterr().err
    with pytest.raises(ValueError, match="finite and positive"):
        exec_candidate_process(
            ["/bin/true"],
            cwd=tmp_path,
            uid=os.getuid(),
            timeout_sec=0,
            address_space_bytes=1024,
        )
