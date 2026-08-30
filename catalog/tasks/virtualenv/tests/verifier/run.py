from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ADAPTER = Path("/tmp/virtualenv-task-adapter.py")


SCENARIOS = (
    "import_version", "module_help", "module_version", "run_exports", "session_parse", "help_flags",
    "basic_create", "created_python_runs", "isolated_prefix", "config_has_home", "config_has_version", "site_packages_exists",
    "default_gitignore", "default_bash_activation", "empty_activators", "no_vcs_ignore", "existing_gitignore_preserved", "prompt_value",
    "prompt_dot", "clear_removes_marker", "system_site_packages_true", "system_site_packages_default_false", "copies_create", "symlinks_create",
    "python_selector", "creator_venv", "app_data_reset", "builtin_discovery", "invalid_discovery", "invalid_interpreter",
    "destination_file_error", "path_separator_error", "pyenvcfg_from_file", "pyenvcfg_write_refresh", "pyenvcfg_prompt_quotes", "cli_run_creates",
)


def invoke(scenario: str) -> dict[str, object]:
    command = [
        "runuser", "-u", "candidate", "--", "env",
        "HOME=/tmp/candidate-home",
        "PYTHONPATH=/tmp/candidate-site:/opt/candidate-dependencies/site",
        "PYTHONDONTWRITEBYTECODE=1", "python", "-B",
        str(ADAPTER), scenario,
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
    except subprocess.TimeoutExpired:
        return {"id": scenario, "status": "failed", "message": "candidate call timed out"}
    if completed.returncode != 0:
        return {"id": scenario, "status": "failed", "message": completed.stderr[-500:] or "child failed"}
    try:
        payload = json.loads(completed.stdout.splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return {"id": scenario, "status": "failed", "message": "child returned no JSON"}
    if payload.get("ok") is True:
        return {"id": scenario, "status": "passed"}
    return {"id": scenario, "status": "failed", "message": str(payload.get("message", "assertion failed"))[:500]}


def main() -> None:
    ADAPTER.unlink(missing_ok=True)
    ADAPTER.write_bytes(Path(__file__).with_name("adapter.py").read_bytes())
    ADAPTER.chmod(0o555)
    leaves = [invoke(item) for item in SCENARIOS]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
