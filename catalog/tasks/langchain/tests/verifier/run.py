from __future__ import annotations

import json
import os
import signal
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Case:
    id: str
    path: str
    expected: Any = None
    contains: str | None = None


CASES = [
    Case(
        "import-middleware-surface",
        "imports.middleware",
        ["ModelCallLimitMiddleware", "PIIMiddleware", "ToolCallLimitMiddleware"],
    ),
    Case(
        "import-structured-surface",
        "imports.structured",
        [
            "AutoStrategy",
            "OutputToolBinding",
            "ProviderStrategy",
            "ProviderStrategyBinding",
            "ToolStrategy",
        ],
    ),
    Case(
        "structured-pydantic-spec-and-binding",
        "structured.pydantic",
        {
            "description": "A contact record.",
            "handle_errors": "retry",
            "kind": "pydantic",
            "name": "Contact",
            "parsed": {"age": 37, "name": "Ada"},
            "properties": ["age", "name"],
            "required": ["name", "age"],
            "tool_description": "A contact record.",
            "tool_message_content": "accepted",
            "tool_name": "Contact",
        },
    ),
    Case("structured-union-names", "structured.union_names", ["Contact", "Product"]),
    Case("structured-union-kinds", "structured.union_kinds", ["pydantic", "pydantic"]),
    Case(
        "structured-oneof-recursive-flatten",
        "structured.one_of_names",
        ["Alpha", "Beta", "Gamma"],
    ),
    Case(
        "structured-oneof-kinds",
        "structured.one_of_kinds",
        ["json_schema", "json_schema", "json_schema"],
    ),
    Case(
        "structured-dataclass-parse",
        "structured.dataclass",
        {"kind": "dataclass", "name": "Point", "parsed": {"x": 2, "y": 5}},
    ),
    Case(
        "structured-typeddict-parse",
        "structured.typeddict",
        {
            "kind": "typeddict",
            "name": "UserRow",
            "parsed": {"active": True, "name": "Grace"},
        },
    ),
    Case(
        "structured-raw-schema-no-validation",
        "structured.raw",
        {
            "description": "Raw payload.",
            "kind": "json_schema",
            "name": "RawPayload",
            "parsed": {"count": "not-an-integer", "extra": True},
        },
    ),
    Case("structured-unsupported-type", "structured.unsupported.type", "ValueError"),
    Case(
        "structured-unsupported-message",
        "structured.unsupported.message",
        contains="Supported types: Pydantic models, dataclasses, TypedDicts, and JSON schema dicts",
    ),
    Case(
        "structured-provider-strict",
        "structured.provider_strict.response_format.json_schema.strict",
        True,
    ),
    Case(
        "structured-provider-format-type",
        "structured.provider_strict.response_format.type",
        "json_schema",
    ),
    Case(
        "structured-provider-schema-name",
        "structured.provider_strict.response_format.json_schema.name",
        "Contact",
    ),
    Case(
        "structured-provider-default-omits-strict",
        "structured.provider_default.response_format.json_schema",
        {
            "name": "Contact",
            "schema": {
                "description": "A contact record.",
                "properties": {
                    "age": {"title": "Age", "type": "integer"},
                    "name": {"title": "Name", "type": "string"},
                },
                "required": ["name", "age"],
                "title": "Contact",
                "type": "object",
            },
        },
    ),
    Case(
        "structured-provider-parse-string",
        "structured.provider_parse_string",
        {"age": 29, "name": "Lin"},
    ),
    Case(
        "structured-provider-parse-blocks",
        "structured.provider_parse_blocks",
        {"age": 31, "name": "Jo"},
    ),
    Case("structured-provider-invalid-json-type", "structured.provider_invalid_json.type", "ValueError"),
    Case(
        "structured-provider-invalid-json-message",
        "structured.provider_invalid_json.message",
        contains="Native structured output expected valid JSON for Contact",
    ),
    Case(
        "structured-provider-validation-error",
        "structured.provider_invalid_schema.message",
        contains="Failed to parse data to Contact",
    ),
    Case("structured-auto-strategy", "structured.auto", "Contact"),
    Case(
        "structured-multiple-error-context",
        "structured.multiple_error",
        {
            "message": "Model incorrectly returned multiple structured responses (Contact, Product) when only one is expected.",
            "message_id": "ai-1",
            "tool_names": ["Contact", "Product"],
        },
    ),
    Case(
        "structured-validation-error-context",
        "structured.validation_error",
        {
            "message": "Failed to parse structured output for tool 'Contact': invalid age.",
            "message_id": "ai-1",
            "source_type": "ValueError",
            "tool_name": "Contact",
        },
    ),
    Case(
        "pii-email-matches",
        "pii.email",
        [
            {"end": 21, "start": 8, "type": "email", "value": "a@example.com"},
            {
                "end": 52,
                "start": 26,
                "type": "email",
                "value": "b.test+tag@sub.example.org",
            },
        ],
    ),
    Case("pii-email-invalid", "pii.email_none", []),
    Case(
        "pii-card-spaces",
        "pii.card_spaces",
        [{"end": 23, "start": 4, "type": "credit_card", "value": "4111 1111 1111 1111"}],
    ),
    Case(
        "pii-card-dashes",
        "pii.card_dashes",
        [{"end": 23, "start": 4, "type": "credit_card", "value": "4111-1111-1111-1111"}],
    ),
    Case("pii-card-luhn-rejection", "pii.card_invalid", []),
    Case(
        "pii-ip-validation",
        "pii.ip",
        [{"end": 17, "start": 6, "type": "ip", "value": "192.168.1.9"}],
    ),
    Case(
        "pii-mac-detection",
        "pii.mac",
        [{"end": 21, "start": 4, "type": "mac_address", "value": "00:1A:2B:3C:4D:5E"}],
    ),
    Case(
        "pii-url-detection",
        "pii.url",
        [
            {"end": 29, "start": 4, "type": "url", "value": "https://example.com/a?q=1"},
            {"end": 47, "start": 30, "type": "url", "value": "www.example.org/x"},
            {"end": 73, "start": 52, "type": "url", "value": "docs.example.net/page"},
        ],
    ),
    Case("pii-bare-domain-rejection", "pii.url_bare_none", []),
    Case(
        "pii-middleware-init",
        "pii.middleware_init",
        {"name": "PIIMiddleware[email]", "pii_type": "email", "strategy": "redact"},
    ),
    Case("pii-redact", "pii.redact_content", "mail [REDACTED_EMAIL] now"),
    Case("pii-mask-email", "pii.mask_email", "mail ada@****.com now"),
    Case("pii-mask-card", "pii.mask_card", "****-****-****-1111"),
    Case("pii-mask-ip", "pii.mask_ip", "*.*.*.40"),
    Case("pii-mask-mac", "pii.mask_mac", "**:**:**:**:**:5E"),
    Case("pii-mask-url", "pii.mask_url", "[MASKED_URL]"),
    Case("pii-hash", "pii.hash_email", "<email_hash:b5fc85e5>"),
    Case("pii-custom-regex", "pii.custom_regex", "open [REDACTED_TICKET] today"),
    Case("pii-unknown-type", "pii.unknown.type", "ValueError"),
    Case(
        "pii-unknown-message",
        "pii.unknown.message",
        contains="Unknown PII type: unknown",
    ),
    Case("pii-before-preserves-original", "pii.before.original_last", "new new@example.com"),
    Case(
        "pii-before-last-user",
        "pii.before.update.messages",
        [
            {
                "content": "old old@example.com",
                "id": "h-old",
                "name": "old",
                "status": None,
                "tool_call_id": None,
                "type": "human",
            },
            {
                "content": "ready",
                "id": "a-1",
                "name": None,
                "status": None,
                "tool_call_id": None,
                "type": "ai",
            },
            {
                "content": "new [REDACTED_EMAIL]",
                "id": "h-new",
                "name": "new",
                "status": None,
                "tool_call_id": None,
                "type": "human",
            },
        ],
    ),
    Case("pii-before-no-match", "pii.before_none", None),
    Case("pii-before-disabled", "pii.before_disabled", None),
    Case("pii-tool-result-mask", "pii.tool_result.messages.1.content", "card **** **** **** 1111"),
    Case("pii-tool-result-identity", "pii.tool_result.messages.1.tool_call_id", "call-1"),
    Case("pii-after-hash", "pii.after.messages.0.content", "send to <email_hash:b5fc85e5>"),
    Case("pii-after-identity", "pii.after.messages.0.id", "out-1"),
    Case("pii-block-type", "pii.block.type", "PIIDetectionError"),
    Case("pii-block-export", "pii.block.is_exported", True),
    Case("pii-block-context", "pii.block.pii_type", "email"),
    Case(
        "pii-block-matches",
        "pii.block.matches",
        [{"end": 18, "start": 5, "type": "email", "value": "x@example.com"}],
    ),
    Case("pii-async-before", "pii.async_before.messages.0.content", "async [REDACTED_EMAIL]"),
    Case("model-limit-missing", "model_limit.missing_limits.type", "ValueError"),
    Case(
        "model-limit-invalid-behavior",
        "model_limit.invalid_behavior.message",
        "Invalid exit_behavior: continue. Must be 'end' or 'error'",
    ),
    Case(
        "model-limit-attributes",
        "model_limit.attributes",
        {"exit_behavior": "end", "run_limit": 2, "thread_limit": 3},
    ),
    Case("model-limit-before-below", "model_limit.before_below", None),
    Case(
        "model-limit-after-increment",
        "model_limit.after",
        {"run_model_call_count": 2, "thread_model_call_count": 3},
    ),
    Case(
        "model-limit-after-zero",
        "model_limit.after_zero",
        {"run_model_call_count": 1, "thread_model_call_count": 1},
    ),
    Case("model-limit-end-jump", "model_limit.before_end.jump_to", "end"),
    Case(
        "model-limit-end-message",
        "model_limit.before_end.messages.0.content",
        "Model call limits exceeded: run limit (2/2)",
    ),
    Case(
        "model-limit-error-context",
        "model_limit.before_error",
        {
            "is_exported": True,
            "message": "Model call limits exceeded: run limit (1/1)",
            "run_count": 1,
            "run_limit": 1,
            "thread_count": 4,
            "thread_limit": None,
            "type": "ModelCallLimitExceededError",
        },
    ),
    Case(
        "model-limit-async-after",
        "model_limit.async_after",
        {"run_model_call_count": 1, "thread_model_call_count": 1},
    ),
    Case("tool-limit-missing", "tool_limit.missing_limits.type", "ValueError"),
    Case(
        "tool-limit-invalid-behavior",
        "tool_limit.invalid_behavior.message",
        contains="Must be one of ('continue', 'error', 'end')",
    ),
    Case(
        "tool-limit-invalid-order",
        "tool_limit.invalid_order.message",
        contains="run_limit (2) cannot exceed thread_limit (1)",
    ),
    Case(
        "tool-limit-attributes",
        "tool_limit.attributes",
        {
            "exit_behavior": "continue",
            "name": "ToolCallLimitMiddleware",
            "named_name": "ToolCallLimitMiddleware[search]",
            "run_limit": 2,
            "thread_limit": 3,
        },
    ),
    Case("tool-limit-no-messages", "tool_limit.no_messages", None),
    Case("tool-limit-no-calls", "tool_limit.no_calls", None),
    Case(
        "tool-limit-allowed-counts",
        "tool_limit.allowed",
        {
            "run_tool_call_count": {"__all__": 2},
            "thread_tool_call_count": {"__all__": 2},
        },
    ),
    Case(
        "tool-limit-named-filter",
        "tool_limit.named_filter",
        {"run_tool_call_count": {"search": 1}, "thread_tool_call_count": {"search": 1}},
    ),
    Case("tool-limit-continue-thread", "tool_limit.continue.thread_tool_call_count.__all__", 1),
    Case("tool-limit-continue-run", "tool_limit.continue.run_tool_call_count.__all__", 2),
    Case("tool-limit-continue-blocked-id", "tool_limit.continue.messages.0.tool_call_id", "s2"),
    Case("tool-limit-continue-status", "tool_limit.continue.messages.0.status", "error"),
    Case("tool-limit-end-jump", "tool_limit.end.jump_to", "end"),
    Case("tool-limit-end-thread-reset", "tool_limit.end.thread_tool_call_count.__all__", 0),
    Case("tool-limit-end-run-attempts", "tool_limit.end.run_tool_call_count.__all__", 2),
    Case("tool-limit-end-blocked-id", "tool_limit.end.messages.0.tool_call_id", "s2"),
    Case("tool-limit-end-pending-id", "tool_limit.end.messages.1.tool_call_id", "s1"),
    Case(
        "tool-limit-end-final-message",
        "tool_limit.end.messages.2.content",
        "Tool call limit reached: run limit exceeded (2/1 calls).",
    ),
    Case(
        "tool-limit-error-context",
        "tool_limit.error",
        {
            "is_exported": True,
            "message": "'search' tool call limit reached: run limit exceeded (1/0 calls).",
            "run_count": 1,
            "run_limit": 0,
            "thread_count": 1,
            "thread_limit": None,
            "tool_name": "search",
            "type": "ToolCallLimitExceededError",
        },
    ),
    Case(
        "tool-limit-existing-counts",
        "tool_limit.existing_counts",
        {
            "run_tool_call_count": {"__all__": 2},
            "thread_tool_call_count": {"__all__": 3},
        },
    ),
    Case(
        "tool-limit-async-allowed",
        "tool_limit.async_allowed",
        {
            "run_tool_call_count": {"__all__": 1},
            "thread_tool_call_count": {"__all__": 1},
        },
    ),
]


def lookup(value: Any, path: str) -> Any:
    current = value
    for component in path.split("."):
        if isinstance(current, list):
            current = current[int(component)]
        elif isinstance(current, dict):
            current = current[component]
        else:
            raise KeyError(path)
    return current


def run_child() -> tuple[dict[str, Any] | None, str | None]:
    verifier_root = Path(__file__).resolve().parent
    child_source = (verifier_root / "child.py").read_bytes()
    child_path = Path("/tmp/langchain-candidate-adapter.py")
    child_path.write_bytes(child_source)
    os.chown(child_path, 10001, 10001)
    os.chmod(child_path, 0o500)
    Path("/tmp/candidate-home").mkdir(exist_ok=True)
    os.chown("/tmp/candidate-home", 10001, 10001)

    command = [
        "runuser",
        "-u",
        "candidate",
        "--",
        "env",
        "HOME=/tmp/candidate-home",
        "PYTHONDONTWRITEBYTECODE=1",
        "prlimit",
        "--as=1073741824",
        "--cpu=20",
        "--fsize=4194304",
        "--nofile=64",
        "--nproc=32",
        "--",
        "python",
        "-I",
        str(child_path),
    ]
    with tempfile.TemporaryDirectory(prefix="langchain-verifier-") as temporary:
        stdout_path = Path(temporary) / "stdout"
        stderr_path = Path(temporary) / "stderr"
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            try:
                returncode = process.wait(timeout=25)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=5)
                return None, "candidate adapter timed out"
        stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace")[-2000:]
        if returncode != 0:
            return None, f"candidate adapter exited {returncode}: {stderr_text}"
        stdout_text = stdout_path.read_text(encoding="utf-8", errors="replace")
        if len(stdout_text.encode("utf-8")) > 4 * 1024 * 1024:
            return None, "candidate adapter output exceeded limit"
        lines = [line for line in stdout_text.splitlines() if line.strip()]
        if not lines:
            return None, "candidate adapter produced no output"
        try:
            payload = json.loads(lines[-1])
        except json.JSONDecodeError as exc:
            return None, f"candidate adapter output was not JSON: {exc}"
        if not isinstance(payload, dict):
            return None, "candidate adapter payload was not an object"
        return payload, None


def main() -> None:
    payload, fatal = run_child()
    leaves = []
    for case in CASES:
        message = ""
        passed = False
        if fatal is not None:
            message = fatal
        else:
            try:
                actual = lookup(payload, case.path)
                if case.contains is not None:
                    passed = isinstance(actual, str) and case.contains in actual
                else:
                    passed = actual == case.expected
                if not passed:
                    message = f"unexpected value at {case.path}"
            except (KeyError, IndexError, TypeError, ValueError):
                message = f"missing or invalid value at {case.path}"
        leaf = {"id": case.id, "status": "passed" if passed else "failed"}
        if message:
            leaf["message"] = message[:500]
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
