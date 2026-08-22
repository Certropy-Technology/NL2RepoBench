from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]


def _load_pi_launcher():
    spec = importlib.util.spec_from_file_location(
        "run_model_from_pi", ROOT / "scripts/run_model_from_pi.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
    environment_index = arguments.index("-e")
    assert arguments[environment_index + 1] == (
        "nl2repobench.harbor_docker:StdinSecretDockerEnvironment"
    )
    assert all(not argument.startswith("LLM_API_KEY=") for argument in arguments)
    assert "test-secret" not in "\n".join(arguments)
    assert "test-secret" not in completed.stdout
    assert "test-secret" not in completed.stderr
    assert "agent_timeout_seconds=18000" in completed.stdout


def test_stdin_secret_environment_keeps_secret_out_of_docker_argv() -> None:
    secret = "sentinel-secret-never-print"
    probe = subprocess.run(
        [
            str(ROOT / "harbor-runner/.venv/bin/python"),
            "-c",
            (
                "import json, os, subprocess, sys; "
                "from harbor.environments.docker.docker import DockerEnvironment; "
                "from nl2repobench.harbor_docker import "
                "StdinSecretDockerEnvironment,_SECRET_WRAPPER,_build_secret_exec; "
                "secret=os.environ['PROBE_SECRET']; "
                "argv,payload=_build_secret_exec(command='echo ok',"
                "public_env={'PUBLIC':'value'},secret_env={'LLM_API_KEY':secret},"
                "cwd='/workspace',user=10001); "
                "assert secret not in '\\n'.join(argv); "
                "assert json.loads(payload)['LLM_API_KEY']==secret; "
                "DockerEnvironment._compose_env_vars=lambda self,include_os_env=True:"
                "{'LLM_API_KEY':secret,'PUBLIC':'value'}; "
                "obj=object.__new__(StdinSecretDockerEnvironment); "
                "assert obj._compose_env_vars()=={'PUBLIC':'value'}; "
                "child=subprocess.run([sys.executable,'-c',_SECRET_WRAPPER,"
                "'test -n \"$LLM_API_KEY\" && echo child-ok'],"
                "input=payload,capture_output=True); "
                "assert child.returncode==0 and child.stdout.strip()==b'child-ok'; "
                "print('ok')"
            ),
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "PROBE_SECRET": secret,
            "PYTHONPATH": str(ROOT / "src"),
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert probe.returncode == 0, probe.stderr
    assert probe.stdout.strip() == "ok"
    assert secret not in probe.stdout
    assert secret not in probe.stderr


def test_agent_log_redaction_removes_secret_bytes(tmp_path: Path) -> None:
    secret = "sentinel-secret-never-print"
    log = tmp_path / "agent.log"
    log.write_text(f"before {secret} after", encoding="utf-8")
    probe = subprocess.run(
        [
            str(ROOT / "harbor-runner/.venv/bin/python"),
            "-c",
            (
                "import os; from pathlib import Path; "
                "from nl2repobench.harbor_openhands import _redact_tree; "
                "assert _redact_tree(Path(os.environ['PROBE_ROOT']),"
                "os.environ['PROBE_SECRET'])==1"
            ),
        ],
        cwd=ROOT,
        env={
            **os.environ,
            "PROBE_ROOT": str(tmp_path),
            "PROBE_SECRET": secret,
            "PYTHONPATH": str(ROOT / "src"),
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert probe.returncode == 0, probe.stderr
    assert secret not in log.read_text(encoding="utf-8")
    assert "[REDACTED]" in log.read_text(encoding="utf-8")


def test_pi_launcher_resolves_only_requested_provider_model(tmp_path: Path) -> None:
    launcher = _load_pi_launcher()
    models = tmp_path / "models.json"
    models.write_text(
        """{
  "providers": {
    "relay": {
      "baseUrl": "https://example.invalid/v1",
      "apiKey": "sentinel-secret",
      "models": [{"id": "test-model"}]
    }
  }
}
""",
        encoding="utf-8",
    )
    models.chmod(0o600)

    base_url, api_key = launcher.provider_credentials(models, "relay", "test-model")

    assert base_url == "https://example.invalid/v1"
    assert api_key == "sentinel-secret"
    with __import__("pytest").raises(ValueError, match="not configured"):
        launcher.provider_credentials(models, "relay", "another-model")
