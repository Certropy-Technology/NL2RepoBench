from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess


ROOT = Path("/tests/verifier")


def main() -> None:
    client = Path("/tmp/pydantic-settings-client.py")
    cases_runner = Path("/tmp/pydantic-settings-cases.py")
    cases_output = Path("/tmp/pydantic-settings-cases.json")
    shutil.copyfile(ROOT / "candidate_client.py", client)
    shutil.copyfile(ROOT / "run_cases.py", cases_runner)
    cases_runner.write_text(
        cases_runner.read_text(encoding="utf-8").replace(
            "env={'PYTHONNOUSERSITE': '1'}",
            "env={'PYTHONNOUSERSITE': '1', 'PYTHONPATH': '/tmp/candidate-site:/opt/candidate-dependencies/site'}",
        ),
        encoding="utf-8",
    )
    cases_output.write_text("", encoding="utf-8")
    os.chown(cases_output, 10001, 10001)
    cases_output.chmod(0o660)
    for path in (client, cases_runner):
        path.chmod(0o555)
    environment = {
        **os.environ,
        "PYTHONNOUSERSITE": "1",
        "PYTHONPATH": "/tmp/candidate-site:/opt/candidate-dependencies/site",
    }
    completed = subprocess.run(
        [
            "runuser",
            "-u",
            "candidate",
            "--",
            "env",
            "PYTHONNOUSERSITE=1",
            "PYTHONPATH=/tmp/candidate-site:/opt/candidate-dependencies/site",
            "/usr/local/bin/python",
            str(cases_runner),
            "--python",
            "/usr/local/bin/python",
            "--client",
            str(client),
            "--output",
            str(cases_output),
        ],
        cwd="/workspace" if Path("/workspace").is_dir() else None,
        env=environment,
        capture_output=True,
        text=True,
        timeout=360,
        check=False,
    )
    if completed.returncode != 0 or not cases_output.is_file():
        print(completed.stderr[-4000:], file=os.sys.stderr)
        raise SystemExit(70)
    records = json.loads(cases_output.read_text(encoding="utf-8"))
    if not isinstance(records, list) or len(records) != 20:
        raise SystemExit(70)
    leaves = [
        {
            "id": str(record["name"]),
            "status": "passed" if record.get("passed") is True else "failed",
            "message": "" if record.get("passed") is True else str(record.get("detail", "failed"))[:512],
        }
        for record in records
    ]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
