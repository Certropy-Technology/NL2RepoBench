from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_model_queue_bounds_concurrency_and_aggregates_failure(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy2(ROOT / "scripts/run_model_queue.sh", scripts / "run_model_queue.sh")
    (scripts / "cleanup_harbor_trials.py").write_text(
        "#!/usr/bin/env python3\n", encoding="utf-8"
    )
    fake_runner = scripts / "run_harbor_model.sh"
    fake_runner.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
state=${STATE_DIR:?}
exec 9>\"$state/lock\"
flock 9
active=$(cat \"$state/active\")
active=$((active + 1))
printf '%s' \"$active\" >\"$state/active\"
max=$(cat \"$state/max\")
if (( active > max )); then printf '%s' \"$active\" >\"$state/max\"; fi
flock -u 9
sleep 0.15
exec 9>\"$state/lock\"
flock 9
active=$(cat \"$state/active\")
printf '%s' \"$((active - 1))\" >\"$state/active\"
flock -u 9
[[ \"$TASK_ID\" != c ]]
""",
        encoding="utf-8",
    )
    fake_runner.chmod(0o755)
    state = tmp_path / "state"
    state.mkdir()
    (state / "active").write_text("0", encoding="utf-8")
    (state / "max").write_text("0", encoding="utf-8")
    run_root = tmp_path / "runs"
    env = {
        **os.environ,
        "TASKS": "a,b,c,d",
        "MODEL": "test/model",
        "LLM_BASE_URL": "https://example.invalid",
        "LLM_API_KEY": "not-used-by-fake",
        "RUN_ROOT": str(run_root),
        "RUN_PREFIX": "queue-test",
        "LOCK_ROOT": str(tmp_path / "locks"),
        "MAX_CONCURRENCY": "2",
        "STATE_DIR": str(state),
        "PATH": f"{scripts.parent}:{os.environ['PATH']}",
    }
    result = subprocess.run(
        ["bash", str(scripts / "run_model_queue.sh")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert (state / "max").read_text(encoding="utf-8") == "2"
    assert "failure[c]" in (run_root / "queue.log").read_text(encoding="utf-8")


def test_model_queue_handles_sigterm_without_unbound_finished_pid(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy2(ROOT / "scripts/run_model_queue.sh", scripts / "run_model_queue.sh")
    (scripts / "cleanup_harbor_trials.py").write_text(
        "#!/usr/bin/env python3\n", encoding="utf-8"
    )
    fake_runner = scripts / "run_harbor_model.sh"
    fake_runner.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\nsleep 30\n",
        encoding="utf-8",
    )
    fake_runner.chmod(0o755)
    run_root = tmp_path / "runs"
    env = {
        **os.environ,
        "TASKS": "a,b",
        "MODEL": "test/model",
        "LLM_BASE_URL": "https://example.invalid",
        "LLM_API_KEY": "not-used-by-fake",
        "RUN_ROOT": str(run_root),
        "RUN_PREFIX": "term-test",
        "LOCK_ROOT": str(tmp_path / "locks"),
        "MAX_CONCURRENCY": "2",
        "PATH": f"{scripts.parent}:{os.environ['PATH']}",
    }
    process = subprocess.Popen(
        ["bash", str(scripts / "run_model_queue.sh")],
        cwd=tmp_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        import time

        time.sleep(0.2)
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate()

    assert process.returncode == 130
    assert "finished_pid: unbound variable" not in stderr
    assert "queue_interrupted=" in stdout
