"""JSON command-line wrapper for the shared candidate subprocess primitive."""

from __future__ import annotations

import base64
import binascii
import json
import re
import sys
from pathlib import Path
from typing import Any

from .subprocess_supervisor import (
    SCHEMA_VERSION,
    CandidateCommand,
    CandidateProcessPolicy,
    ProcessContractError,
    SubprocessLimits,
    run_candidate_process,
)

EXIT_OK = 0
EXIT_MALFORMED = 64
EXIT_INTERNAL = 70
EXIT_CLEANUP = 75
_REQUEST_ID = re.compile(r"^[0-9a-f]{32}$")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _json_request(raw: bytes) -> dict[str, Any]:
    if len(raw) > 1 * 1024 * 1024:
        raise ProcessContractError("request JSON exceeds limit")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ProcessContractError("invalid request JSON") from exc
    if not isinstance(value, dict):
        raise ProcessContractError("request JSON must be an object")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise ProcessContractError("unsupported request schema")
    return value


def _path_tuple(values: Any) -> tuple[Path, ...]:
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ProcessContractError("policy roots must be string arrays")
    return tuple(Path(value) for value in values)


def _request(
    value: dict[str, Any]
) -> tuple[str, CandidateCommand, SubprocessLimits, CandidateProcessPolicy, bytes]:
    request_id = value.get("request_id")
    if not isinstance(request_id, str) or not _REQUEST_ID.fullmatch(request_id):
        raise ProcessContractError("invalid request_id")
    command_data = value.get("command")
    limits_data = value.get("limits")
    policy_data = value.get("policy")
    if (
        not isinstance(command_data, dict)
        or not isinstance(limits_data, dict)
        or not isinstance(policy_data, dict)
    ):
        raise ProcessContractError("request command, limits, and policy are required")
    argv = command_data.get("argv")
    cwd = command_data.get("cwd")
    if (
        not isinstance(argv, list)
        or not all(isinstance(item, str) for item in argv)
        or not isinstance(cwd, str)
    ):
        raise ProcessContractError("invalid candidate command")
    environment = command_data.get("environment", [])
    if not isinstance(environment, list):
        raise ProcessContractError("invalid candidate environment")
    env_pairs: list[tuple[str, str]] = []
    for item in environment:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or not all(isinstance(x, str) for x in item)
        ):
            raise ProcessContractError("invalid candidate environment")
        env_pairs.append((item[0], item[1]))
    command = CandidateCommand(tuple(argv), cwd, tuple(env_pairs))
    limits = SubprocessLimits(**{key: limits_data[key] for key in (
        "timeout_sec", "cpu_sec", "max_stdin_bytes", "max_output_bytes", "max_file_bytes",
        "max_open_files", "uid", "gid", "max_processes",
    ) if key in limits_data})
    policy = CandidateProcessPolicy(
        task_id=policy_data["task_id"],
        staging_root=Path(policy_data["staging_root"]),
        read_only_roots=_path_tuple(policy_data["read_only_roots"]),
        write_root=Path(policy_data["write_root"]),
        allowed_executable_roots=_path_tuple(policy_data["allowed_executable_roots"]),
        allowed_environment_names=frozenset(policy_data.get("allowed_environment_names", [])),
        require_no_new_privs=policy_data.get("require_no_new_privs", True),
        require_empty_capabilities=policy_data.get("require_empty_capabilities", True),
    )
    encoded = value.get("stdin_base64", "")
    if not isinstance(encoded, str):
        raise ProcessContractError("stdin_base64 must be a string")
    try:
        stdin_data = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (ValueError, binascii.Error, UnicodeEncodeError) as exc:
        raise ProcessContractError("invalid stdin_base64") from exc
    if value.get("context") not in {"install", "call", "bridge"}:
        raise ProcessContractError("invalid request context")
    return request_id, command, limits, policy, stdin_data


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(1 * 1024 * 1024 + 1)
        request_id, command, limits, policy, stdin_data = _request(_json_request(raw))
        result = run_candidate_process(
            command, limits, policy, request_id=request_id, stdin_data=stdin_data
        )
        encoded = json.dumps(result.as_dict(), sort_keys=True, separators=(",", ":"))
        if len(encoded.encode("utf-8")) > 20 * 1024 * 1024:
            return EXIT_INTERNAL
        sys.stdout.write(encoded + "\n")
        sys.stdout.flush()
        return EXIT_CLEANUP if not result.cleanup_complete else EXIT_OK
    except (ProcessContractError, KeyError, TypeError, ValueError):
        return EXIT_MALFORMED
    except OSError:
        return EXIT_INTERNAL
    except Exception:
        return EXIT_INTERNAL


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["EXIT_CLEANUP", "EXIT_INTERNAL", "EXIT_MALFORMED", "EXIT_OK", "main"]
