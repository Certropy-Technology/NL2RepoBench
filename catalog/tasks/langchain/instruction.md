# Project Description

Create an installable Python package named `langchain` that implements a deterministic, offline-safe subset of LangChain's agent support APIs. The package must provide structured-output strategies and bindings, PII handling middleware, and model/tool call-limit middleware. Model-provider integrations, network calls, graph execution, and the full `create_agent` factory are outside this task.

# Supports

- Python 3.10 or newer.
- A root `pyproject.toml` with project name `langchain` and an importable `langchain` package.
- Runtime dependencies compatible with `langchain-core>=1.6.0,<2.0.0`, `langgraph>=1.2.11,<1.3.0`, and `pydantic>=2.7.4,<3.0.0`.
- Local installation with `python -m pip install .` without downloading dependencies during evaluation.
- Public imports from `langchain.agents.structured_output` and `langchain.agents.middleware`, including the APIs described below.

# API Usage Guide

## Structured output strategies

The module `langchain.agents.structured_output` must expose these classes:

```python
class ToolStrategy(Generic[SchemaT]):
    def __init__(
        self,
        schema: type[SchemaT] | types.UnionType | dict[str, Any],
        *,
        tool_message_content: str | None = None,
        handle_errors: bool | str | type[Exception] |
            tuple[type[Exception], ...] | Callable[[Exception], str] = True,
    ) -> None: ...

class ProviderStrategy(Generic[SchemaT]):
    def __init__(
        self,
        schema: type[SchemaT] | dict[str, Any],
        *,
        strict: bool | None = None,
    ) -> None: ...
    def to_model_kwargs(self) -> dict[str, Any]: ...

@dataclass
class OutputToolBinding(Generic[SchemaT]):
    @classmethod
    def from_schema_spec(cls, schema_spec): ...
    def parse(self, tool_args: dict[str, Any]) -> SchemaT | dict[str, Any]: ...

@dataclass
class ProviderStrategyBinding(Generic[SchemaT]):
    @classmethod
    def from_schema_spec(cls, schema_spec): ...
    def parse(self, response: langchain_core.messages.AIMessage) -> SchemaT | dict[str, Any]: ...

class AutoStrategy(Generic[SchemaT]):
    def __init__(self, schema: type[SchemaT] | dict[str, Any]) -> None: ...
```

Supported schemas are Pydantic `BaseModel` subclasses, standard-library dataclasses, `TypedDict` classes, and raw JSON Schema dictionaries. A schema specification exposes `schema`, `name`, `description`, `schema_kind`, `json_schema`, and `strict`. Names default to the Python class name or a JSON Schema `title`; descriptions default to the class docstring or JSON Schema `description`. Unsupported schema objects raise `ValueError`.

`ToolStrategy.schema_specs` contains one specification per schema. Python unions are recursively flattened. A raw JSON Schema containing `oneOf` is also flattened recursively into one specification per leaf. `tool_message_content` and `handle_errors` are retained unchanged.

`OutputToolBinding.from_schema_spec` creates a `langchain_core.tools.StructuredTool` whose name, description, and argument schema match the specification. `parse` validates and constructs Pydantic, dataclass, and `TypedDict` values. Validation failures raise `ValueError`. Raw JSON Schema dictionaries are descriptive only: their input mappings are returned unchanged without local validation.

`ProviderStrategy.to_model_kwargs()` returns provider-native response format kwargs shaped as:

```python
{
    "response_format": {
        "type": "json_schema",
        "json_schema": {"name": name, "schema": json_schema},
    }
}
```

When `strict=True`, the inner `json_schema` mapping also contains `"strict": True`; false or omitted strictness does not add that key.

`ProviderStrategyBinding.parse` accepts an `AIMessage`. String content is parsed directly as JSON. List content is converted to text by concatenating `{"type": "text", "text": ...}` blocks, dictionary blocks with a string `content` field, and string representations of other items. Invalid JSON and schema validation failures raise `ValueError`.

The module must also expose `StructuredOutputError`, `MultipleStructuredOutputsError`, and `StructuredOutputValidationError`. The two concrete errors retain their constructor context as public attributes and provide descriptive messages.

## PII detection and middleware

`langchain.agents.middleware.pii` must expose:

```python
detect_email(content: str) -> list[PIIMatch]
detect_credit_card(content: str) -> list[PIIMatch]
detect_ip(content: str) -> list[PIIMatch]
detect_mac_address(content: str) -> list[PIIMatch]
detect_url(content: str) -> list[PIIMatch]

class PIIMiddleware:
    def __init__(
        self,
        pii_type: str,
        *,
        strategy: Literal["block", "redact", "mask", "hash"] = "redact",
        detector: Callable[[str], list[PIIMatch]] | str | None = None,
        apply_to_input: bool = True,
        apply_to_output: bool = False,
        apply_to_tool_results: bool = False,
    ) -> None: ...
```

Every `PIIMatch` is a mapping with `type`, `value`, `start`, and exclusive `end`. Detection order follows text order. Credit cards must pass the Luhn checksum. IP detection covers valid dotted IPv4 values and rejects out-of-range candidates. URL detection accepts `http` and `https` URLs, `www.` names, and bare domains with paths; a bare domain without a path is not a match.

Built-in `pii_type` values are `email`, `credit_card`, `ip`, `mac_address`, and `url`. Any other type requires a detector callable or regular-expression string. The middleware's `name` is `PIIMiddleware[<type>]`.

Strategies behave as follows:

- `redact`: replace each match with `[REDACTED_<UPPERCASE_TYPE>]`.
- `mask`: preserve recognizable non-sensitive portions. Emails preserve the local part and top-level domain; cards preserve the final four digits; IPv4 values preserve the final octet; MAC addresses preserve the final byte; URLs become `[MASKED_URL]`.
- `hash`: replace a match with `<type_hash:xxxxxxxx>`, where the suffix is the first eight hexadecimal characters of SHA-256 over the exact matched text.
- `block`: raise `PIIDetectionError`, which exposes `pii_type` and the complete `matches` list.

`before_model(state, runtime)` processes the last `HumanMessage` when `apply_to_input=True`. When `apply_to_tool_results=True`, it also processes every `ToolMessage` after the last `AIMessage`. `after_model(state, runtime)` processes the last `AIMessage` when `apply_to_output=True`. Modified hooks return `{"messages": new_messages}`; otherwise they return `None`. Existing message IDs, names, tool-call IDs, and AI tool calls are preserved. Async hook variants have the same observable result.

## Model call limits

`langchain.agents.middleware` re-exports `ModelCallLimitMiddleware`; its exception class is imported from `langchain.agents.middleware.model_call_limit`. The middleware has this constructor:

```python
ModelCallLimitMiddleware(
    *,
    thread_limit: int | None = None,
    run_limit: int | None = None,
    exit_behavior: Literal["end", "error"] = "end",
)
```

At least one limit is required. Invalid exit behavior raises `ValueError`. `after_model` increments `thread_model_call_count` and `run_model_call_count`, treating missing values as zero. `before_model` compares current counts to configured limits. Below the limits it returns `None`. At or above a limit, `end` returns `jump_to="end"` with one explanatory `AIMessage`; `error` raises `ModelCallLimitExceededError`. The error exposes counts and configured limits. Async hooks match synchronous hooks.

## Tool call limits

`langchain.agents.middleware` re-exports `ToolCallLimitMiddleware`; its exception class is imported from `langchain.agents.middleware.tool_call_limit`. The middleware has this constructor:

```python
ToolCallLimitMiddleware(
    *,
    tool_name: str | None = None,
    thread_limit: int | None = None,
    run_limit: int | None = None,
    exit_behavior: Literal["continue", "error", "end"] = "continue",
)
```

At least one limit is required. When both are present, `run_limit` cannot exceed `thread_limit`. A `tool_name` limits only matching calls; `None` tracks all calls under the `"__all__"` count key. The middleware examines tool calls on the last `AIMessage`.

Allowed calls increment both count maps. Blocked attempts do not increment the thread count but do increment the run count. `continue` returns error-status `ToolMessage` objects for blocked calls. `error` raises `ToolCallLimitExceededError` with counts, limits, and the optional tool name. `end` returns `jump_to="end"`, error `ToolMessage` objects for blocked and otherwise pending calls, and a final explanatory `AIMessage`; because no calls execute in that batch, its thread count remains at the pre-batch value. Empty message histories, histories without an AI message, and AI messages without matching tool calls return `None`. Async behavior matches synchronous behavior.

# Implementation Notes

- Keep the API import-compatible with the paths above. Re-export `PIIMiddleware`, `PIIDetectionError`, `ModelCallLimitMiddleware`, and `ToolCallLimitMiddleware` from `langchain.agents.middleware`; detector functions and call-limit exception classes remain available from their documented specific modules.
- Use `langchain_core` message and tool types and `langgraph` middleware state conventions; do not replace them with task-specific lookalikes.
- PII scanning and strategy application must be deterministic and must preserve match offsets relative to the original input.
- The structured-output JSON Schema produced by Pydantic/dataclass/`TypedDict` adapters must remain compatible with Pydantic v2.
- Runtime behavior in this task is fully local. Do not call model providers, remote APIs, package indexes, or source hosts.
