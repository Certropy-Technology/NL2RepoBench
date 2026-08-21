# mypy: disable-error-code="import-not-found,misc,untyped-decorator"
"""Harbor OpenHands SDK adapter with file-backed instructions.

Harbor 0.21's bundled SDK adapter places the complete instruction in the
``docker compose exec`` argv. Large legacy NL2Repo instructions can exceed
the host ``ARG_MAX`` limit. This adapter uploads the instruction and passes a
short file path to a tiny wrapper, preserving the SDK runner and all Harbor
phase boundaries.
"""

from __future__ import annotations

import json
from pathlib import Path

from harbor.agents.installed import openhands_sdk
from harbor.agents.installed.base import (
    ApiInternalServerError,
    ApiOverloadedError,
    ErrorPattern,
    with_prompt_template,
)
from harbor.agents.installed.openhands_sdk import OpenHandsSDK
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from typing_extensions import override

FILE_RUNNER = r"""#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys

instruction_path = Path(sys.argv[1])
instruction = instruction_path.read_text(encoding="utf-8")
sys.argv = [
    "/installed-agent/run_agent.py",
    "--instruction",
    instruction,
    *sys.argv[2:],
]
runpy.run_path("/installed-agent/run_agent.py", run_name="__main__")
"""


class OpenHandsSDKFileInstruction(OpenHandsSDK):  # pragma: no cover - Harbor integration
    """OpenHands SDK adapter that avoids a giant exec argument.

    Extends the stock error taxonomy so gateway/proxy failures from the
    OpenAI-compatible relay classify as retryable infrastructure errors
    instead of the generic ``NonZeroAgentExitCodeError`` (which Harbor must
    treat as a model failure).
    """

    ERROR_PATTERNS = [
        *OpenHandsSDK.ERROR_PATTERNS,
        ErrorPattern(
            r"upstream request failed", ApiInternalServerError
        ),
        ErrorPattern(r"BadGatewayError|badgateway", ApiInternalServerError),
        ErrorPattern(r"\"type\":\s*\"upstream_error\"", ApiOverloadedError),
        # Anthropic transport-level disconnect: relay/proxy kills the stream
        # before any response; must retry as infrastructure, not model failure.
        ErrorPattern(
            r"Server disconnected without sending a response",
            ApiInternalServerError,
        ),
        ErrorPattern(
            r"InternalServerError.*AnthropicException",
            ApiInternalServerError,
        ),
        # LiteLLM sometimes wraps a completed/transport-broken relay response
        # as a generic APIError or exposes the TLS EOF directly.  These are
        # retryable gateway failures, not evidence that the candidate failed.
        ErrorPattern(
            r"APIError.*OpenAIException|OpenAIException.*UNEXPECTED_EOF",
            ApiInternalServerError,
        ),
        ErrorPattern(r"UNEXPECTED_EOF_WHILE_READING", ApiInternalServerError),
    ]

    @override
    @with_prompt_template
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        llm_api_key = self._get_env("LLM_API_KEY")
        if llm_api_key is None:
            raise ValueError("LLM_API_KEY environment variable must be set")

        env: dict[str, str] = {"LLM_API_KEY": llm_api_key}
        base_url = self._get_env("LLM_BASE_URL")
        if base_url is not None:
            env["LLM_BASE_URL"] = base_url
        if self.model_name:
            env["LLM_MODEL"] = self.model_name
        else:
            model = self._get_env("LLM_MODEL")
            if model is None:
                raise ValueError("No LLM model specified")
            env["LLM_MODEL"] = model

        env["AGENT_LOGS_DIR"] = "/logs/agent"
        env["TRAJECTORY_PATH"] = "/logs/agent/trajectory.json"
        env["LOAD_SKILLS"] = "1" if self._load_skills else "0"
        env["SKILL_PATHS"] = ":".join(self._skill_paths)
        if self._collect_token_ids:
            env["LITELLM_EXTRA_BODY"] = json.dumps({"return_token_ids": True})
        if self._max_iterations is not None:
            env["MAX_ITERATIONS"] = str(self._max_iterations)
        if self._temperature is not None:
            env["LLM_TEMPERATURE"] = str(self._temperature)
        if self._reasoning_effort is not None:
            env["LLM_REASONING_EFFORT"] = str(self._reasoning_effort)
        # LLM-level retry/timeout knobs forwarded to the SDK runner.
        for name in (
            "LLM_NUM_RETRIES",
            "LLM_RETRY_MIN_WAIT",
            "LLM_RETRY_MAX_WAIT",
            "LLM_TIMEOUT",
        ):
            value = self._get_env(name)
            if value is not None:
                env[name] = value

        # Keep the same MCP serialization contract as Harbor's bundled adapter.
        if self.mcp_servers:
            servers: list[dict[str, object]] = []
            for server in self.mcp_servers:
                entry: dict[str, object] = {
                    "name": server.name,
                    "transport": server.transport,
                }
                if server.transport == "stdio":
                    if server.command:
                        entry["command"] = server.command
                    if server.args:
                        entry["args"] = server.args
                elif server.url:
                    entry["url"] = server.url
                servers.append(entry)
            env["MCP_SERVERS_JSON"] = json.dumps(servers)

        instruction_file = self.logs_dir / "instruction.md"
        runner_file = self.logs_dir / "run_agent_file.py"
        sdk_runner_file = self.logs_dir / "run_agent.py"
        instruction_file.write_text(instruction, encoding="utf-8")
        runner_file.write_text(FILE_RUNNER, encoding="utf-8")
        runner_source = (
            Path(openhands_sdk.__file__)
            .with_name("openhands_sdk_runner.py")
            .read_text(encoding="utf-8")
        )
        marker = """    llm_kwargs: dict[str, Any] = {
        "model": model,
        "api_key": api_key,
        "base_url": base_url,
    }
"""
        replacement = (
            marker
            + """    reasoning_effort = os.environ.get("LLM_REASONING_EFFORT")
    if reasoning_effort:
        llm_kwargs["reasoning_effort"] = reasoning_effort
    retry_env_map = {
        "LLM_NUM_RETRIES": ("num_retries", int),
        "LLM_RETRY_MIN_WAIT": ("retry_min_wait", int),
        "LLM_RETRY_MAX_WAIT": ("retry_max_wait", int),
        "LLM_TIMEOUT": ("timeout", int),
    }
    for env_name, (kwarg, cast) in retry_env_map.items():
        env_value = os.environ.get(env_name)
        if env_value:
            llm_kwargs[kwarg] = cast(env_value)
"""
        )
        if marker not in runner_source:
            raise RuntimeError("OpenHands SDK runner changed; reasoning patch is unsafe")
        sdk_runner_file.write_text(
            runner_source.replace(marker, replacement, 1),
            encoding="utf-8",
        )
        await environment.upload_file(
            source_path=instruction_file,
            target_path="/installed-agent/instruction.md",
        )
        await environment.upload_file(
            source_path=runner_file,
            target_path="/installed-agent/run_agent_file.py",
        )
        await environment.upload_file(
            source_path=sdk_runner_file,
            target_path="/installed-agent/run_agent.py",
        )
        await environment.exec(
            command="chmod 0555 /installed-agent/instruction.md /installed-agent/run_agent_file.py",
            user="root",
        )

        command = (
            "/opt/openhands-sdk-venv/bin/python /installed-agent/run_agent_file.py "
            "/installed-agent/instruction.md "
            '--logs-dir="$AGENT_LOGS_DIR" '
            '--trajectory-path="$TRAJECTORY_PATH" '
            "2>&1 | stdbuf -oL tee /logs/agent/openhands_sdk.txt"
        )
        await self.exec_as_agent(environment, command=command, env=env)
