from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_model_runner_uses_harbor_native_five_hour_agent_timeout(tmp_path: Path) -> None:
    task_root = tmp_path / "catalog/tasks/demo/harbor"
    task_root.mkdir(parents=True)
    (task_root / "task.toml").write_text(
        'schema_version = "1.4"\n[agent]\ntimeout_sec = 3600.0\n',
        encoding="utf-8",
    )
    (tmp_path / "harbor-runner").mkdir()

    capture = tmp_path / "uv-arguments.txt"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_uv = fake_bin / "uv"
    fake_uv.write_text(
        '#!/usr/bin/env bash\nprintf "%s\\n" "$@" > "$CAPTURE"\n',
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)

    env = os.environ.copy()
    env.update(
        {
            "AGENT_TIMEOUT_SECONDS": "18000",
            "CAPTURE": str(capture),
            "LLM_API_KEY": "test-secret",
            "LLM_BASE_URL": "https://example.invalid/v1",
            "MODEL": "openai/test-model",
            "PATH": f"{fake_bin}:{env['PATH']}",
            "TASK_ID": "demo",
        }
    )
    completed = subprocess.run(
        ["bash", str(ROOT / "scripts/run_harbor_model.sh")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    arguments = capture.read_text(encoding="utf-8").splitlines()
    multiplier_index = arguments.index("--agent-timeout-multiplier")
    assert arguments[multiplier_index + 1] == "5"
    assert "timeout" not in arguments
    assert "--verifier-timeout-multiplier" not in arguments
    assert "agent_timeout_seconds=18000" in completed.stdout
