from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import tempfile
from pathlib import Path

from nl2repobench.verification.process_cleanup import terminate_uid_processes

RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
PREFIX = "JARACO_CONTEXT_RESULT="
MAX_OUTPUT_BYTES = 1024 * 1024

# Each entry is (leaf suffix, result path, expected value). A scenario is run once
# in the candidate process and may establish several independently scored facts.
CHECKS: dict[str, list[tuple[str, tuple[object, ...], object]]] = {
    "exports": [
        ("names", ("all_present",), True),
        ("module", ("module",), "jaraco.context"),
        ("tarfile-module", ("tarfile_module",), "tarfile"),
    ],
    "metadata": [
        ("version", ("version",), "6.1.3.dev6+gbfcb95c78"),
        ("typed-marker", ("typed_marker",), True),
        ("pushd-parameters", ("pushd_parameters",), ["dir"]),
        ("tarball-default", ("tarball_target_default",), None),
        ("on-interrupt-signature", ("on_interrupt_signature",), ["POSITIONAL_ONLY", 1]),
    ],
    "pushd": [("behavior", (), {"inside": [True, True], "restored": True})],
    "pushd_exception": [("exception-cleanup", (), {"error": "sentinel", "restored": True})],
    "temp_dir": [
        (
            "custom-and-default-removal",
            (),
            {
                "custom_exists": True,
                "custom_remover_called": True,
                "custom_still_exists": True,
                "default_removed": True,
            },
        )
    ],
    "robust_remover": [
        ("linux-rmtree", ("is_rmtree",), True),
        ("robust-temp-dir", ("removed",), True),
    ],
    "compose": [
        (
            "order-and-result",
            (),
            {
                "events": ["inner-enter", "outer-enter", "body", "outer-exit", "inner-exit"],
                "result": 8,
            },
        )
    ],
    "exception_trap": [
        ("capture", (), {"bool": True, "tb": True, "type": "ValueError", "value": "bad"})
    ],
    "exception_trap_nonmatch": [
        ("propagation", (), {"bool": False, "propagated": "KeyError", "type": None})
    ],
    "trap_decorators": [
        (
            "raises-passes-metadata",
            (),
            {"doc": "fails doc", "name": "fails", "passes": True, "raises": True},
        )
    ],
    "suppress": [
        (
            "context-and-decorator",
            (),
            {"context": True, "decorator_returned": None, "subclass": True},
        )
    ],
    "on_interrupt": [
        ("error", ("error",), {"code": 7, "type": "SystemExit"}),
        ("ignore", ("ignore",), {"code": None, "type": "KeyboardInterrupt"}),
        ("suppress", ("suppress",), None),
        ("other-exception", ("other",), "ValueError"),
    ],
    "strip_filter": [("strip", (), {"name": "inner.txt", "same": True})],
    "filter_compose": [
        ("right-to-left", (), {"events": [["right", "x"], ["left", "xR"]], "result": "xRL"})
    ],
    "tar_filter_cases": [
        ("legitimate", (0,), "ok"),
        ("normalized", (1,), "FileExistsError"),
        ("tmp-escape", (2,), "OutsideDestinationError"),
        ("home-escape", (3,), "OutsideDestinationError"),
        ("parent-escape", (4,), "OutsideDestinationError"),
    ],
    "tarball": [
        ("extract", ("inside",), [True, "payload"]),
        ("cleanup", ("cleaned",), True),
    ],
    "tarball_default_target": [
        ("derived-target", ("value",), ["thing", "thing", True]),
        ("cleanup", ("cleaned",), True),
    ],
    "tarball_error": [("error-cleanup", (), {"cleaned": True, "type": "RuntimeError"})],
    "tarball_cwd": [
        ("cwd", ("value",), [True, True]),
        ("restore-cleanup", ("after",), [True, True]),
    ],
    "repo_context": [
        (
            "git-command",
            ("command",),
            [
                "git",
                "clone",
                "https://example.invalid/repo.git",
                "<destination>",
                "--branch",
                "stable",
            ],
        ),
        ("quiet", ("quiet",), [True, True]),
        ("yield", ("yielded",), True),
    ],
    "repo_context_hg": [
        (
            "hg-command",
            ("command",),
            ["hg", "clone", "https://example.invalid/repo", "<destination>"],
        ),
        ("not-quiet", ("quiet",), [True, True]),
    ],
    "remove_readonly": [
        ("retry", ("retry",), {"called": True, "mode": "0o777"}),
        ("reraises", ("reraised",), "PermissionError"),
    ],
}


def _lookup(value: object, path: tuple[object, ...]) -> object:
    current = value
    for part in path:
        if isinstance(part, int) and isinstance(current, list):
            current = current[part]
        elif isinstance(part, str) and isinstance(current, dict):
            current = current[part]
        else:
            raise KeyError(path)
    return current


def invoke(adapter: Path, scenario: str) -> dict[str, object]:
    command = [
        RUNUSER,
        "-u",
        "candidate",
        "--",
        "env",
        "HOME=/tmp/candidate-build/home",
        "TMPDIR=/tmp/candidate-build/tmp",
        "PYTHONDONTWRITEBYTECODE=1",
        "python",
        "-I",
        "-B",
        str(adapter),
        "--candidate-site",
        "/tmp/candidate-site",
        "--scenario",
        scenario,
    ]
    with tempfile.TemporaryDirectory(prefix="jaraco-context-verifier-") as output_dir:
        stdout_path = Path(output_dir, "stdout")
        stderr_path = Path(output_dir, "stderr")
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(
                command,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            try:
                returncode = process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
                return {"ok": False, "type": "CandidateTimeout", "message": scenario}
            finally:
                terminate_uid_processes(10001)
        stdout_data = stdout_path.read_bytes()[:MAX_OUTPUT_BYTES]
        stderr_data = stderr_path.read_bytes()[:MAX_OUTPUT_BYTES]
    try:
        stdout_text = stdout_data.decode("utf-8")
        stderr_text = stderr_data.decode("utf-8", errors="replace")
    except UnicodeDecodeError as exc:
        return {"ok": False, "type": "CandidateProtocolError", "message": str(exc)}
    lines = [line for line in stdout_text.splitlines() if line.startswith(PREFIX)]
    if returncode != 0 or len(lines) != 1:
        return {"ok": False, "type": "CandidateProcessError", "message": stderr_text[-2000:]}
    try:
        payload = json.loads(lines[0][len(PREFIX) :])
    except json.JSONDecodeError as exc:
        return {"ok": False, "type": "CandidateProtocolError", "message": str(exc)}
    return payload if isinstance(payload, dict) else {"ok": False, "type": "CandidateProtocolError"}


def main() -> int:
    adapter_source = Path(__file__).with_name("adapter.py")
    adapter = Path("/tmp/jaraco-context-adapter.py")
    adapter.write_bytes(adapter_source.read_bytes())
    os.chown(adapter, 10001, 10001)
    os.chmod(adapter, 0o500)
    leaves: list[dict[str, str]] = []
    fatal_result: dict[str, object] | None = None
    try:
        for scenario, checks in CHECKS.items():
            result = fatal_result or invoke(adapter, scenario)
            if scenario == "exports" and result.get("ok") is not True:
                fatal_result = result
            if result.get("ok") is True:
                scenario_value: object = result.get("value")
            else:
                scenario_value = {"type": result.get("type"), "message": result.get("message")}
            for suffix, path, expected in checks:
                try:
                    actual = _lookup(scenario_value, path)
                except (IndexError, KeyError, TypeError):
                    actual = scenario_value
                passed = actual == expected
                leaves.append(
                    {
                        "id": f"jaraco-context/{scenario}/{suffix}",
                        "status": "passed" if passed else "failed",
                        "message": ""
                        if passed
                        else json.dumps(
                            {"actual": actual, "expected": expected}, sort_keys=True, default=str
                        )[:2000],
                    }
                )
    finally:
        adapter.unlink(missing_ok=True)
        terminate_uid_processes(10001)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
