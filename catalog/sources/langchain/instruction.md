# Project Description

Create an installable Python package named `langchain` that implements a deterministic, offline-safe subset of LangChain's agent support APIs. The package must provide structured-output strategies and bindings, PII handling middleware, and model/tool call-limit middleware. Model-provider integrations, network calls, graph execution, and the full `create_agent` factory are outside this task.

# Natural Language Instruction

Create the `langchain` project from an empty `workspace/`. Implement the
documented structured-output, PII middleware, model-call-limit, and
tool-call-limit APIs under the public import paths below. The package must be
installable with the declared metadata, expose the documented names, and use
the installed `langchain_core`, `langgraph`, and `pydantic` types where the
contract calls for them. Keep the implementation local and deterministic.

Do not implement or require provider network calls, graph execution,
`create_agent`, chat-model initialization, shell/file-search middleware, or
other excluded integrations. The requested project is a package, not a copy
of the upstream repository: create only the package modules and build metadata
needed by the public contract and ordinary local use.

# Supports

- Python 3.10 or newer.
- A root `pyproject.toml` with project name `langchain` and an importable `langchain` package.
- Runtime dependencies compatible with `langchain-core>=1.6.0,<2.0.0`, `langgraph>=1.2.11,<1.3.0`, and `pydantic>=2.7.4,<3.0.0`.
- Local installation with `python -m pip install .` without downloading dependencies during evaluation.
- Public imports from `langchain.agents.structured_output` and `langchain.agents.middleware`, including the APIs described below.

# Project Directory Structure

Create a package with this minimum public layout. The module names in this
tree must agree with the import paths in the API guide.

```text
workspace/
├── pyproject.toml
└── langchain/
    ├── __init__.py
    └── agents/
        ├── __init__.py
        ├── structured_output.py
        └── middleware/
            ├── __init__.py
            ├── pii.py
            ├── model_call_limit.py
            └── tool_call_limit.py
```

`pyproject.toml` is the install metadata and must declare the `langchain`
distribution. `langchain/agents/structured_output.py` owns schema strategies,
bindings, and structured-output errors. `middleware/pii.py` owns detectors,
PII matches, and message hooks. The two limit modules own their middleware
classes and exception types; `middleware/__init__.py` provides the documented
re-exports. A root `__init__.py` may expose package metadata but must not move
the documented APIs to an undocumented import path.

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

# Examples

```python
from dataclasses import dataclass
from langchain.agents.structured_output import ToolStrategy

@dataclass
class Answer:
    value: str

strategy = ToolStrategy(Answer)
assert strategy.schema_specs[0].name == "Answer"
```

```python
from langchain.agents.middleware.pii import detect_email, PIIMiddleware

matches = detect_email("send to user@example.com")
assert matches[0]["value"] == "user@example.com"
middleware = PIIMiddleware("email", strategy="redact")
```

# Error Handling and Boundary Conditions

- Unsupported structured-output schema objects raise `ValueError`; malformed
  JSON content and schema validation failures are also reported as
  `ValueError` by the documented bindings.
- Credit-card matches are accepted only when the Luhn checksum succeeds, and
  IP detection rejects dotted candidates with out-of-range octets.
- A PII middleware configured with `strategy="block"` raises
  `PIIDetectionError` with the complete ordered match list; `hash` uses the
  exact matched text and is deterministic.
- Limit middleware constructors reject missing limits and invalid exit
  behavior. Empty message histories and histories without relevant messages
  return `None` from the tool-limit hooks.
- The package must not access the network, current time, random state, or
  external files during these operations. Preserve message IDs, names,
  tool-call IDs, and AI tool calls when hooks return modified messages.
