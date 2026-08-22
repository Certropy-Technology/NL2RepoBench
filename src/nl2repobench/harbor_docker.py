# mypy: disable-error-code="import-not-found,misc"
"""Docker environment with stdin-only delivery for sensitive exec variables."""

from __future__ import annotations

import json
from typing import cast

from harbor.constants import MAIN_SERVICE_NAME
from harbor.environments.base import ExecResult
from harbor.environments.docker.docker import DockerEnvironment

_SECRET_WRAPPER = r"""
import json
import os
import sys

payload = json.load(sys.stdin)
if not isinstance(payload, dict) or not all(
    isinstance(key, str) and isinstance(value, str) for key, value in payload.items()
):
    raise SystemExit(64)
os.environ.update(payload)
os.execv("/bin/bash", ["bash", "-lc", sys.argv[1]])
""".strip()


def _build_secret_exec(
    *,
    command: str,
    public_env: dict[str, str],
    secret_env: dict[str, str],
    cwd: str | None,
    user: str | int | None,
) -> tuple[list[str], bytes]:
    if not secret_env or any(not key or "=" in key for key in secret_env):
        raise ValueError("secret environment requires non-empty variable names")
    overlap = set(public_env).intersection(secret_env)
    if overlap:
        raise ValueError(f"secret variables duplicated in public environment: {sorted(overlap)}")

    exec_command = ["exec", "-T"]
    if cwd:
        exec_command.extend(["-w", cwd])
    for key, value in public_env.items():
        exec_command.extend(["-e", f"{key}={value}"])
    if user is not None:
        exec_command.extend(["-u", str(user)])
    exec_command.extend(
        [
            MAIN_SERVICE_NAME,
            "/opt/openhands-sdk-venv/bin/python",
            "-c",
            _SECRET_WRAPPER,
            command,
        ]
    )
    payload = json.dumps(secret_env, separators=(",", ":")).encode("utf-8")
    return exec_command, payload


class StdinSecretDockerEnvironment(DockerEnvironment):  # pragma: no cover - Harbor integration
    """Deliver selected environment values over stdin, never Docker argv."""

    def _compose_env_vars(self, include_os_env: bool = True) -> dict[str, str]:
        environment = cast(
            dict[str, str],
            super()._compose_env_vars(include_os_env=include_os_env),
        )
        environment.pop("LLM_API_KEY", None)
        return environment

    async def exec_with_stdin_secret(
        self,
        command: str,
        *,
        secret_env: dict[str, str],
        env: dict[str, str] | None = None,
        cwd: str | None = None,
        timeout_sec: int | None = None,
        user: str | int | None = None,
    ) -> ExecResult:
        public_env = self._merge_env(env) or {}
        resolved_cwd = cwd or self.task_env_config.workdir
        resolved_user = self._resolve_user(user)
        exec_command, payload = _build_secret_exec(
            command=command,
            public_env=public_env,
            secret_env=secret_env,
            cwd=resolved_cwd,
            user=resolved_user,
        )
        return await self._run_docker_compose_command(
            exec_command,
            check=False,
            timeout_sec=timeout_sec,
            stdin_data=payload,
            on_output=self._output_callback(),
        )
