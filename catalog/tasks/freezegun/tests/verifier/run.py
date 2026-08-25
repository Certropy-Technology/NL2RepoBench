from __future__ import annotations

import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
EXPECTED = json.loads((ROOT / "expected.json").read_text(encoding="utf-8"))
MAX_OUTPUT_BYTES = 1024 * 1024


def candidate_command(adapter: Path, operation: str) -> list[str]:
    python = "/usr/local/bin/python" if Path("/usr/local/bin/python").is_file() else sys.executable
    command = [
        "env",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        "prlimit",
        "--as=536870912",
        "--cpu=10",
        f"--fsize={MAX_OUTPUT_BYTES}",
        "--nofile=64",
        "--nproc=16",
        "--",
        python,
        "-I",
        str(adapter),
        operation,
    ]
    if os.geteuid() == 0:
        try:
            pwd.getpwnam("candidate")
        except KeyError:
            pass
        else:
            command = ["runuser", "-u", "candidate", "--", *command]
    return command


def run_operation(adapter: Path, operation: str) -> tuple[dict[str, object] | None, str]:
    environment = os.environ.copy()
    environment["NL2REPO_FREEZEGUN_CANDIDATE_SITE"] = environment.get(
        "NL2REPO_FREEZEGUN_CANDIDATE_SITE", "/tmp/candidate-site"
    )
    with tempfile.TemporaryDirectory(prefix="freezegun-verifier-") as temporary:
        stdout_path = Path(temporary) / "stdout"
        stderr_path = Path(temporary) / "stderr"
        try:
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                completed = subprocess.run(
                    candidate_command(adapter, operation),
                    stdout=stdout,
                    stderr=stderr,
                    timeout=5,
                    check=False,
                    env=environment,
                )
        except subprocess.TimeoutExpired:
            return None, "candidate-timeout"
        except (OSError, subprocess.SubprocessError) as exc:
            return None, type(exc).__name__

        stdout_data = stdout_path.read_bytes()
        stderr_data = stderr_path.read_bytes()[:4000]
    if len(stdout_data) > MAX_OUTPUT_BYTES:
        return None, "candidate-output-limit"
    responses = []
    for raw_line in stdout_data.splitlines():
        try:
            response = json.loads(raw_line)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(response, dict) and response.get("id") == operation:
            responses.append(response)
    diagnostic = (
        f"candidate-exit={completed.returncode}; "
        f"stdout-bytes={len(stdout_data)}; "
        f"stderr={stderr_data.decode('utf-8', 'replace')[-1000:]}"
    )
    if len(responses) != 1:
        return None, diagnostic
    return responses[0], diagnostic


def main() -> None:
    adapter = Path("/tmp/freezegun-contract-adapter.py")
    shutil.copyfile(ROOT / "adapter.py", adapter)
    adapter.chmod(0o444)
    leaves = []
    for name, expected in EXPECTED.items():
        response, diagnostic = run_operation(adapter, name)
        passed = (
            isinstance(response, dict)
            and response.get("ok") is True
            and response.get("result") == expected
        )
        leaves.append(
            {
                "id": f"freezegun-contract::{name}",
                "status": "passed" if passed else "failed",
                "message": "" if passed else diagnostic,
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
