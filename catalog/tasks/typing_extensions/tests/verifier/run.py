from __future__ import annotations

import json
import os
from pathlib import Path
import pwd
import shutil
import signal
import subprocess
import sys


VERIFIER_ROOT = Path(__file__).resolve().parent
EXPECTED = json.loads((VERIFIER_ROOT / "expected.json").read_text(encoding="utf-8"))
MAX_RESPONSE_BYTES = 1024 * 1024


def candidate_command(adapter: Path) -> list[str]:
    python = "/usr/local/bin/python" if Path("/usr/local/bin/python").is_file() else sys.executable
    command = [
        "env",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
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
            command = [
                "runuser",
                "-u",
                "candidate",
                "--",
                "prlimit",
                "--as=536870912",
                "--cpu=45",
                f"--fsize={MAX_RESPONSE_BYTES}",
                "--nofile=64",
                "--nproc=32",
                "--",
                *command,
            ]
    return command


def terminate(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_candidate() -> tuple[dict[str, object], str]:
    source = VERIFIER_ROOT / "adapter.py"
    adapter = Path(
        os.environ.get(
            "NL2REPO_TYPING_EXTENSIONS_ADAPTER_COPY",
            "/tmp/typing-extensions-contract-adapter.py",
        )
    )
    stdout_path = Path("/tmp/typing-extensions-contract-stdout.jsonl")
    stderr_path = Path("/tmp/typing-extensions-contract-stderr.txt")
    adapter.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, adapter)
    adapter.chmod(0o444)
    stdout_path.unlink(missing_ok=True)
    stderr_path.unlink(missing_ok=True)

    requests = [{"id": name, "operation": name} for name in EXPECTED]
    payload = "".join(json.dumps(item, sort_keys=True) + "\n" for item in requests)
    environment = os.environ.copy()
    local_site = environment.get("NL2REPO_TYPING_EXTENSIONS_CANDIDATE_SITE")
    if local_site:
        environment["NL2REPO_TYPING_EXTENSIONS_CANDIDATE_SITE"] = local_site

    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(
                candidate_command(adapter),
                stdin=subprocess.PIPE,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
                env=environment,
            )
            try:
                process.communicate(payload.encode("utf-8"), timeout=60)
            except subprocess.TimeoutExpired:
                terminate(process)
                process.wait(timeout=5)
                return {}, "candidate-timeout"
            finally:
                terminate(process)
    except (OSError, subprocess.SubprocessError) as exc:
        return {}, type(exc).__name__

    try:
        if stdout_path.stat().st_size > MAX_RESPONSE_BYTES:
            return {}, "candidate-output-limit"
        output = stdout_path.read_text(encoding="utf-8")
        stderr_tail = stderr_path.read_text(encoding="utf-8", errors="replace")[-1000:]
    except OSError as exc:
        return {}, type(exc).__name__

    responses: dict[str, object] = {}
    duplicates: set[str] = set()
    for line in output.splitlines():
        try:
            response = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(response, dict):
            continue
        response_id = response.get("id")
        if response_id not in EXPECTED:
            continue
        if response_id in responses:
            duplicates.add(response_id)
        else:
            responses[response_id] = response
    for duplicate in duplicates:
        responses.pop(duplicate, None)
    diagnostic = f"candidate-exit={process.returncode}; stderr={stderr_tail}"
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
                "id": f"typing-extensions-runtime::{name}",
                "status": "passed" if passed else "failed",
                "message": "" if passed else diagnostic,
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
