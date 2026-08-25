from __future__ import annotations

import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys


ROOT = Path(__file__).parent
EXPECTED = json.loads((ROOT / "expected.json").read_text(encoding="utf-8"))
MAX_OUTPUT = 1024 * 1024


def command(adapter: Path) -> list[str]:
    python = "/usr/local/bin/python" if Path("/usr/local/bin/python").is_file() else sys.executable
    result = [
        "env", "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1",
        "prlimit", "--as=536870912", "--cpu=90", f"--fsize={MAX_OUTPUT}",
        "--nofile=64", "--nproc=4096", "--", python, "-I", str(adapter),
    ]
    if os.geteuid() == 0:
        try:
            pwd.getpwnam("candidate")
        except KeyError:
            pass
        else:
            result = ["runuser", "-u", "candidate", "--", *result]
    return result


def collect() -> tuple[dict[str, object], str]:
    adapter = Path("/tmp/python-dotenv-contract-adapter.py")
    shutil.copyfile(ROOT / "adapter.py", adapter)
    adapter.chmod(0o444)
    payload = "".join(
        json.dumps({"id": name, "operation": name}, sort_keys=True) + "\n"
        for name in EXPECTED
    )
    env = os.environ.copy()
    env["NL2REPO_DOTENV_CANDIDATE_SITE"] = env.get(
        "NL2REPO_DOTENV_CANDIDATE_SITE", "/tmp/candidate-site"
    )
    try:
        completed = subprocess.run(
            command(adapter), input=payload, text=True, capture_output=True,
            timeout=90, check=False, env=env,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {}, type(exc).__name__
    responses: dict[str, object] = {}
    duplicates: set[str] = set()
    for line in completed.stdout[:MAX_OUTPUT].splitlines():
        try:
            response = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(response, dict) or response.get("id") not in EXPECTED:
            continue
        name = str(response["id"])
        if name in responses:
            duplicates.add(name)
        else:
            responses[name] = response
    for name in duplicates:
        responses.pop(name, None)
    diagnostic = f"exit={completed.returncode}; stderr={completed.stderr[-1200:]}"
    return responses, diagnostic


def main() -> None:
    responses, diagnostic = collect()
    leaves = []
    for name, expected in EXPECTED.items():
        response = responses.get(name)
        passed = isinstance(response, dict) and response.get("ok") is True and response.get("result") == expected
        leaves.append({
            "id": f"python-dotenv-contract::{name}",
            "status": "passed" if passed else "failed",
            "message": "" if passed else diagnostic,
        })
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
