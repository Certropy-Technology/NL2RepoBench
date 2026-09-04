from __future__ import annotations

import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).parent
EXPECTED = json.loads((ROOT / "expected.json").read_text(encoding="utf-8"))
MAX_OUTPUT_BYTES = 1024 * 1024


def candidate_command(adapter: Path) -> list[str]:
    python = "/usr/local/bin/python" if Path("/usr/local/bin/python").is_file() else sys.executable
    command = [
        "env",
        "HOME=/tmp",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        "TMPDIR=/tmp",
        "prlimit",
        "--as=536870912",
        "--cpu=90",
        f"--fsize={MAX_OUTPUT_BYTES}",
        "--nofile=64",
        "--nproc=16",
        "--",
        python,
        "-I",
        str(adapter),
    ]
    if os.geteuid() == 0:
        try:
            pwd.getpwnam("candidate")
        except KeyError:
            pass
        else:
            command = ["runuser", "-u", "candidate", "--", *command]
    return command


def run_candidate() -> tuple[dict[str, object], str]:
    adapter = Path("/tmp/tinydb-contract-adapter.py")
    shutil.copyfile(ROOT / "adapter.py", adapter)
    adapter.chmod(0o444)
    requests = [{"id": name, "operation": name} for name in EXPECTED]
    payload = "".join(json.dumps(item, sort_keys=True) + "\n" for item in requests)
    environment = os.environ.copy()
    environment["NL2REPO_TINYDB_CANDIDATE_SITE"] = environment.get(
        "NL2REPO_TINYDB_CANDIDATE_SITE", "/tmp/candidate-site"
    )
    with tempfile.TemporaryDirectory(prefix="tinydb-verifier-") as temporary:
        stdout_path = Path(temporary) / "stdout"
        stderr_path = Path(temporary) / "stderr"
        try:
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                completed = subprocess.run(
                    candidate_command(adapter),
                    input=payload.encode("utf-8"),
                    stdout=stdout,
                    stderr=stderr,
                    timeout=120,
                    check=False,
                    env=environment,
                )
        except (OSError, subprocess.SubprocessError) as exc:
            return {}, type(exc).__name__
        stdout_data = stdout_path.read_bytes()[:MAX_OUTPUT_BYTES]
        stderr_data = stderr_path.read_bytes()[:4000]

    responses: dict[str, object] = {}
    duplicates: set[str] = set()
    for raw_line in stdout_data.splitlines():
        try:
            response = json.loads(raw_line)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(response, dict) or response.get("id") not in EXPECTED:
            continue
        response_id = str(response["id"])
        if response_id in responses:
            duplicates.add(response_id)
        else:
            responses[response_id] = response
    for response_id in duplicates:
        responses.pop(response_id, None)

    diagnostic = (
        f"candidate-exit={completed.returncode}; "
        f"stdout-bytes={len(stdout_data)}; "
        f"stderr={stderr_data.decode('utf-8', 'replace')[-1000:]}"
    )
    return responses, diagnostic


def main() -> None:
    responses, diagnostic = run_candidate()
    leaves = []
    for name, expected in EXPECTED.items():
        response = responses.get(name)
        passed = (
            isinstance(response, dict)
            and response.get("ok") is True
            and response.get("result") == expected
        )
        leaves.append(
            {
                "id": f"tinydb-contract::{name}",
                "status": "passed" if passed else "failed",
                "message": "" if passed else diagnostic,
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
