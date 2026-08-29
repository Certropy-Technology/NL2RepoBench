from __future__ import annotations

import asyncio
import dataclasses
import json
import sys
from typing import Any

sys.path.insert(0, "/opt/candidate-dependencies/site")
sys.path.insert(0, "/tmp/candidate-site")

from langchain.agents.middleware import (  # noqa: E402
    ModelCallLimitMiddleware,
    PIIDetectionError,
    PIIMiddleware,
    ToolCallLimitMiddleware,
)
from langchain.agents.middleware.model_call_limit import (  # noqa: E402
    ModelCallLimitExceededError,
)
from langchain.agents.middleware.pii import (  # noqa: E402
    detect_credit_card,
    detect_email,
    detect_ip,
    detect_mac_address,
    detect_url,
)
from langchain.agents.middleware.tool_call_limit import (  # noqa: E402
    ToolCallLimitExceededError,
)
from langchain.agents.structured_output import (  # noqa: E402
    AutoStrategy,
    MultipleStructuredOutputsError,
    OutputToolBinding,
    ProviderStrategy,
    ProviderStrategyBinding,
    StructuredOutputValidationError,
    ToolStrategy,
)
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from typing_extensions import TypedDict  # noqa: E402


def message_data(message: Any) -> dict[str, Any]:
    return {
        "content": message.content,
        "id": message.id,
        "name": message.name,
        "status": getattr(message, "status", None),
        "tool_call_id": getattr(message, "tool_call_id", None),
        "type": message.type,
    }


def update_data(update: dict[str, Any] | None) -> dict[str, Any] | None:
    if update is None:
        return None
    result = {key: value for key, value in update.items() if key != "messages"}
    if "messages" in update:
        result["messages"] = [message_data(message) for message in update["messages"]]
    return result


class Contact(BaseModel):
    """A contact record."""

    name: str
    age: int


class Product(BaseModel):
    """A product record."""

    sku: str


@dataclasses.dataclass
class Point:
    """A two-dimensional point."""

    x: int
    y: int


class UserRow(TypedDict):
    """A typed user mapping."""

    name: str
    active: bool


def probe_structured() -> dict[str, Any]:
    result: dict[str, Any] = {}

    strategy = ToolStrategy(Contact, tool_message_content="accepted", handle_errors="retry")
    spec = strategy.schema_specs[0]
    binding = OutputToolBinding.from_schema_spec(spec)
    parsed = binding.parse({"name": "Ada", "age": "37"})
    result["pydantic"] = {
        "description": spec.description,
        "handle_errors": strategy.handle_errors,
        "kind": spec.schema_kind,
        "name": spec.name,
        "parsed": parsed.model_dump(),
        "properties": sorted(spec.json_schema["properties"]),
        "required": spec.json_schema["required"],
        "tool_description": binding.tool.description,
        "tool_message_content": strategy.tool_message_content,
        "tool_name": binding.tool.name,
    }

    union_strategy = ToolStrategy(Contact | Product)
    result["union_names"] = [item.name for item in union_strategy.schema_specs]
    result["union_kinds"] = [item.schema_kind for item in union_strategy.schema_specs]

    one_of = ToolStrategy(
        {
            "oneOf": [
                {"title": "Alpha", "type": "object", "properties": {"a": {"type": "string"}}},
                {
                    "oneOf": [
                        {"title": "Beta", "type": "object"},
                        {"title": "Gamma", "type": "object"},
                    ]
                },
            ]
        }
    )
    result["one_of_names"] = [item.name for item in one_of.schema_specs]
    result["one_of_kinds"] = [item.schema_kind for item in one_of.schema_specs]

    point_spec = ToolStrategy(Point).schema_specs[0]
    point = OutputToolBinding.from_schema_spec(point_spec).parse({"x": "2", "y": 5})
    result["dataclass"] = {
        "kind": point_spec.schema_kind,
        "name": point_spec.name,
        "parsed": dataclasses.asdict(point),
    }

    typed_spec = ToolStrategy(UserRow).schema_specs[0]
    typed = OutputToolBinding.from_schema_spec(typed_spec).parse(
        {"name": "Grace", "active": "true"}
    )
    result["typeddict"] = {
        "kind": typed_spec.schema_kind,
        "name": typed_spec.name,
        "parsed": typed,
    }

    raw_schema = {
        "title": "RawPayload",
        "description": "Raw payload.",
        "type": "object",
        "properties": {"count": {"type": "integer"}},
    }
    raw_spec = ToolStrategy(raw_schema).schema_specs[0]
    raw_input = {"count": "not-an-integer", "extra": True}
    result["raw"] = {
        "description": raw_spec.description,
        "kind": raw_spec.schema_kind,
        "name": raw_spec.name,
        "parsed": OutputToolBinding.from_schema_spec(raw_spec).parse(raw_input),
    }

    try:
        ToolStrategy(42)
    except Exception as exc:
        result["unsupported"] = {"type": type(exc).__name__, "message": str(exc)}

    provider = ProviderStrategy(Contact, strict=True)
    result["provider_strict"] = provider.to_model_kwargs()
    result["provider_default"] = ProviderStrategy(Contact).to_model_kwargs()

    provider_binding = ProviderStrategyBinding.from_schema_spec(provider.schema_spec)
    parsed_provider = provider_binding.parse(AIMessage(content='{"name":"Lin","age":29}'))
    result["provider_parse_string"] = parsed_provider.model_dump()
    parsed_blocks = provider_binding.parse(
        AIMessage(
            content=[
                {"type": "text", "text": '{"name":"Jo"'},
                {"content": ',"age":31}'},
            ]
        )
    )
    result["provider_parse_blocks"] = parsed_blocks.model_dump()
    for key, message in (
        ("provider_invalid_json", AIMessage(content="not-json")),
        ("provider_invalid_schema", AIMessage(content='{"name":"No age"}')),
    ):
        try:
            provider_binding.parse(message)
        except Exception as exc:
            result[key] = {"type": type(exc).__name__, "message": str(exc)}

    result["auto"] = AutoStrategy(Contact).schema.__name__

    ai_message = AIMessage(content="bad", id="ai-1")
    multiple = MultipleStructuredOutputsError(["Contact", "Product"], ai_message)
    validation_source = ValueError("invalid age")
    validation = StructuredOutputValidationError("Contact", validation_source, ai_message)
    result["multiple_error"] = {
        "message": str(multiple),
        "tool_names": multiple.tool_names,
        "message_id": multiple.ai_message.id,
    }
    result["validation_error"] = {
        "message": str(validation),
        "tool_name": validation.tool_name,
        "source_type": type(validation.source).__name__,
        "message_id": validation.ai_message.id,
    }
    return result


def probe_pii() -> dict[str, Any]:
    result: dict[str, Any] = {}
    result["email"] = detect_email("Contact a@example.com and b.test+tag@sub.example.org")
    result["email_none"] = detect_email("not-an-email@example and plain text")
    result["card_spaces"] = detect_credit_card("pay 4111 1111 1111 1111 now")
    result["card_dashes"] = detect_credit_card("pay 4111-1111-1111-1111 now")
    result["card_invalid"] = detect_credit_card("pay 4111 1111 1111 1112 now")
    result["ip"] = detect_ip("hosts 192.168.1.9 and 999.1.1.1")
    result["mac"] = detect_mac_address("mac 00:1A:2B:3C:4D:5E")
    result["url"] = detect_url(
        "see https://example.com/a?q=1 www.example.org/x and docs.example.net/page"
    )
    result["url_bare_none"] = detect_url("mention example.com without a path")

    redactor = PIIMiddleware("email", strategy="redact")
    result["middleware_init"] = {
        "name": redactor.name,
        "pii_type": redactor.pii_type,
        "strategy": redactor.strategy,
    }
    result["redact_content"] = redactor._process_content("mail ada@example.com now")[0]
    result["mask_email"] = PIIMiddleware("email", strategy="mask")._process_content(
        "mail ada@example.com now"
    )[0]
    result["mask_card"] = PIIMiddleware("credit_card", strategy="mask")._process_content(
        "4111-1111-1111-1111"
    )[0]
    result["mask_ip"] = PIIMiddleware("ip", strategy="mask")._process_content(
        "10.20.30.40"
    )[0]
    result["mask_mac"] = PIIMiddleware("mac_address", strategy="mask")._process_content(
        "00:1A:2B:3C:4D:5E"
    )[0]
    result["mask_url"] = PIIMiddleware("url", strategy="mask")._process_content(
        "https://example.com/private"
    )[0]
    result["hash_email"] = PIIMiddleware("email", strategy="hash")._process_content(
        "ada@example.com"
    )[0]

    custom = PIIMiddleware("ticket", detector=r"TKT-\d{4}", strategy="redact")
    result["custom_regex"] = custom._process_content("open TKT-2048 today")[0]
    try:
        PIIMiddleware("unknown")
    except Exception as exc:
        result["unknown"] = {"type": type(exc).__name__, "message": str(exc)}

    before_messages = [
        HumanMessage(content="old old@example.com", id="h-old", name="old"),
        AIMessage(content="ready", id="a-1"),
        HumanMessage(content="new new@example.com", id="h-new", name="new"),
    ]
    before = redactor.before_model({"messages": before_messages}, None)
    result["before"] = {
        "original_last": before_messages[-1].content,
        "update": update_data(before),
    }
    result["before_none"] = redactor.before_model(
        {"messages": [HumanMessage(content="no pii", id="h-1")]}, None
    )

    disabled = PIIMiddleware("email", apply_to_input=False)
    result["before_disabled"] = disabled.before_model(
        {"messages": [HumanMessage(content="x@example.com")]}, None
    )

    tool_middleware = PIIMiddleware(
        "credit_card", strategy="mask", apply_to_input=False, apply_to_tool_results=True
    )
    tool_messages = [
        AIMessage(
            content="calling",
            tool_calls=[{"name": "pay", "args": {}, "id": "call-1", "type": "tool_call"}],
        ),
        ToolMessage(
            content="card 4111 1111 1111 1111", tool_call_id="call-1", id="tool-1"
        ),
    ]
    result["tool_result"] = update_data(
        tool_middleware.before_model({"messages": tool_messages}, None)
    )

    output_middleware = PIIMiddleware(
        "email", strategy="hash", apply_to_input=False, apply_to_output=True
    )
    output_messages = [AIMessage(content="send to ada@example.com", id="out-1", name="bot")]
    result["after"] = update_data(
        output_middleware.after_model({"messages": output_messages}, None)
    )

    try:
        PIIMiddleware("email", strategy="block").before_model(
            {"messages": [HumanMessage(content="stop x@example.com")]}, None
        )
    except Exception as exc:
        result["block"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "pii_type": getattr(exc, "pii_type", None),
            "matches": getattr(exc, "matches", None),
            "is_exported": isinstance(exc, PIIDetectionError),
        }

    result["async_before"] = update_data(
        asyncio.run(
            redactor.abefore_model(
                {"messages": [HumanMessage(content="async x@example.com", id="async-1")]},
                None,
            )
        )
    )
    return result


def probe_model_limit() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, kwargs in (
        ("missing_limits", {}),
        ("invalid_behavior", {"run_limit": 1, "exit_behavior": "continue"}),
    ):
        try:
            ModelCallLimitMiddleware(**kwargs)
        except Exception as exc:
            result[key] = {"type": type(exc).__name__, "message": str(exc)}

    limiter = ModelCallLimitMiddleware(thread_limit=3, run_limit=2)
    result["attributes"] = {
        "exit_behavior": limiter.exit_behavior,
        "run_limit": limiter.run_limit,
        "thread_limit": limiter.thread_limit,
    }
    result["before_below"] = limiter.before_model(
        {"messages": [], "thread_model_call_count": 2, "run_model_call_count": 1}, None
    )
    result["after"] = limiter.after_model(
        {"messages": [], "thread_model_call_count": 2, "run_model_call_count": 1}, None
    )
    result["after_zero"] = limiter.after_model({"messages": []}, None)

    end_update = limiter.before_model(
        {"messages": [], "thread_model_call_count": 2, "run_model_call_count": 2}, None
    )
    result["before_end"] = update_data(end_update)

    try:
        ModelCallLimitMiddleware(run_limit=1, exit_behavior="error").before_model(
            {"messages": [], "thread_model_call_count": 4, "run_model_call_count": 1}, None
        )
    except Exception as exc:
        result["before_error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "is_exported": isinstance(exc, ModelCallLimitExceededError),
            "thread_count": getattr(exc, "thread_count", None),
            "run_count": getattr(exc, "run_count", None),
            "thread_limit": getattr(exc, "thread_limit", None),
            "run_limit": getattr(exc, "run_limit", None),
        }

    result["async_after"] = asyncio.run(limiter.aafter_model({"messages": []}, None))
    return result


def tool_call(name: str, identifier: str) -> dict[str, Any]:
    return {"name": name, "args": {"q": identifier}, "id": identifier, "type": "tool_call"}


def probe_tool_limit() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, kwargs in (
        ("missing_limits", {}),
        ("invalid_behavior", {"run_limit": 1, "exit_behavior": "stop"}),
        ("invalid_order", {"thread_limit": 1, "run_limit": 2}),
    ):
        try:
            ToolCallLimitMiddleware(**kwargs)
        except Exception as exc:
            result[key] = {"type": type(exc).__name__, "message": str(exc)}

    limiter = ToolCallLimitMiddleware(thread_limit=3, run_limit=2)
    named = ToolCallLimitMiddleware(tool_name="search", run_limit=2)
    result["attributes"] = {
        "exit_behavior": limiter.exit_behavior,
        "name": limiter.name,
        "named_name": named.name,
        "run_limit": limiter.run_limit,
        "thread_limit": limiter.thread_limit,
    }
    result["no_messages"] = limiter.after_model({"messages": []}, None)
    result["no_calls"] = limiter.after_model(
        {"messages": [HumanMessage(content="x"), AIMessage(content="done")]}, None
    )

    allowed_message = AIMessage(
        content="",
        tool_calls=[tool_call("search", "s1"), tool_call("calc", "c1")],
    )
    result["allowed"] = update_data(limiter.after_model({"messages": [allowed_message]}, None))
    result["named_filter"] = update_data(
        named.after_model({"messages": [allowed_message]}, None)
    )

    batch = AIMessage(
        content="",
        tool_calls=[tool_call("search", "s1"), tool_call("search", "s2")],
    )
    continuing = ToolCallLimitMiddleware(run_limit=1, exit_behavior="continue")
    result["continue"] = update_data(continuing.after_model({"messages": [batch]}, None))

    ending = ToolCallLimitMiddleware(run_limit=1, exit_behavior="end")
    result["end"] = update_data(ending.after_model({"messages": [batch]}, None))

    try:
        ToolCallLimitMiddleware(
            tool_name="search", run_limit=0, exit_behavior="error"
        ).after_model({"messages": [AIMessage(content="", tool_calls=[tool_call("search", "s1")])]}, None)
    except Exception as exc:
        result["error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "is_exported": isinstance(exc, ToolCallLimitExceededError),
            "thread_count": getattr(exc, "thread_count", None),
            "run_count": getattr(exc, "run_count", None),
            "thread_limit": getattr(exc, "thread_limit", None),
            "run_limit": getattr(exc, "run_limit", None),
            "tool_name": getattr(exc, "tool_name", None),
        }

    existing = ToolCallLimitMiddleware(thread_limit=4, run_limit=4)
    result["existing_counts"] = update_data(
        existing.after_model(
            {
                "messages": [AIMessage(content="", tool_calls=[tool_call("search", "s3")])],
                "thread_tool_call_count": {"__all__": 2},
                "run_tool_call_count": {"__all__": 1},
            },
            None,
        )
    )
    result["async_allowed"] = update_data(
        asyncio.run(
            limiter.aafter_model(
                {"messages": [AIMessage(content="", tool_calls=[tool_call("search", "a1")])]},
                None,
            )
        )
    )
    return result


def main() -> None:
    payload = {
        "imports": {
            "middleware": sorted(
                [
                    ModelCallLimitMiddleware.__name__,
                    PIIMiddleware.__name__,
                    ToolCallLimitMiddleware.__name__,
                ]
            ),
            "structured": sorted(
                [
                    AutoStrategy.__name__,
                    OutputToolBinding.__name__,
                    ProviderStrategy.__name__,
                    ProviderStrategyBinding.__name__,
                    ToolStrategy.__name__,
                ]
            ),
        },
        "model_limit": probe_model_limit(),
        "pii": probe_pii(),
        "structured": probe_structured(),
        "tool_limit": probe_tool_limit(),
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
