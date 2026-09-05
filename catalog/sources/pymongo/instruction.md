# pymongo

## Project Description

Build an installable `pymongo` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `pymongo`; public import package begins at `pymongo`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Package Version`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `JSON Utilities`: preserve the documented object or module behavior, including state and side effects.
3. `bson.json_util.dumps(obj: Any, *args: Any, **kwargs: Any) -> str`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `'{"second": 2, "first": "caf\\u00e9"}'`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `pymongo`; public import package begins at `pymongo`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `dnspython==2.8.0`, `flit-core==3.12.0`, `hatch-requirements-txt==0.4.1`, `hatchling==1.27.0`, `packaging==26.3`, `pathspec==1.1.1`, `pluggy==1.6.0`, `setuptools==80.9.0`, `trove-classifiers==2026.6.1.19`, `wheel==0.45.1`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── packages/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

### Package Version

`pymongo.__version__` is the exact string `"4.18.0.dev0"`.

### JSON Utilities

#### `bson.json_util.dumps(obj: Any, *args: Any, **kwargs: Any) -> str`

For dictionaries, lists, strings, numbers, booleans, and `None`, return the
same JSON spelling as Python's default `json.dumps`: include the default spaces
after separators, preserve dictionary insertion order, and escape non-ASCII
characters by default. Nested values retain their shape.

Example:

```python
from bson import json_util

json_util.dumps({"second": 2, "first": "caf\u00e9"})
# '{"second": 2, "first": "caf\\u00e9"}'
```

#### `bson.json_util.loads(s: str | bytes | bytearray, *args: Any, **kwargs: Any) -> Any`

Parse JSON objects, arrays, strings, integers, floating-point numbers,
booleans, and null into their corresponding Python values. Leading and
trailing whitespace is accepted. Invalid JSON raises the underlying
`json.JSONDecodeError`; do not return a partial result.

### ObjectId Validation

#### `bson.objectid.ObjectId.is_valid(oid: Any) -> bool`

Return `True` for a 24-character hexadecimal string, accepting upper- or
lowercase hexadecimal digits. Return `False` for malformed values, including
wrong-length strings, non-hexadecimal text, 12-character text, integers, and
`None`. Validation does not raise for these malformed inputs.

### Host Parsing

#### `pymongo.uri_parser.parse_host(entity: str, default_port: int | None = 27017) -> tuple[str, int | None]`

Parse one host and return `(hostname, port)`. Lowercase the returned hostname.
Use `default_port` when no explicit port is present. Accept bracketed IPv6
literals and return the address without brackets. Explicit ports must be base-10
integers from 1 through 65535; zero, larger values, and non-numeric values raise
`ValueError`.

#### `pymongo.uri_parser.split_hosts(hosts: str, default_port: int | None = 27017) -> list[tuple[str, int | None]]`

Split a comma-separated host list in input order and apply `parse_host` to each
entry. Empty entries, including a doubled comma or a trailing comma, raise
`pymongo.errors.ConfigurationError`.

### MongoDB URI Parsing

#### `pymongo.uri_parser.parse_uri(uri: str, default_port: int | None = 27017, validate: bool = True, warn: bool = False, normalize: bool = True, connect_timeout: float | None = None, srv_service_name: str | None = None, srv_max_hosts: int | None = None) -> dict[str, Any]`

Support `mongodb://` URIs using literal hostnames, IPv4 addresses, bracketed
IPv6 addresses, and comma-separated host lists. This task does not require
`mongodb+srv://` or DNS resolution.

The returned dictionary has exactly these keys:

- `nodelist`: ordered `(hostname, port)` pairs;
- `username` and `password`: URL-decoded strings or `None`;
- `database`: the decoded database name or `None`;
- `collection`: the collection suffix after `database.`, or `None`;
- `options`: a dictionary of normalized option names and converted values;
- `fqdn`: `None` for the supported literal-host `mongodb://` form.

Accept both ampersand and semicolon option separators. Normalize recognized
option names to the driver's canonical spelling. Convert recognized booleans to
`bool`; convert `connectTimeoutMS` milliseconds to seconds as `float` (for
example, `2500` becomes `2.5`). An unsupported scheme raises
`pymongo.errors.InvalidURI`. An out-of-range explicit port raises `ValueError`.

### Scalar Validators

The following functions are imported from `pymongo.common`. Their `option`
argument is used to identify invalid input in the exception message.

- `validate_boolean(option: str, value: Any) -> bool` accepts exactly `True` or
  `False`; other values raise `TypeError`.
- `validate_integer(option: str, value: Any) -> int` accepts integer values;
  non-integers raise `TypeError`.
- `validate_string(option: str, value: Any) -> str` accepts strings;
  non-strings raise `TypeError`.
- `validate_string_or_none(option: str, value: Any) -> str | None` accepts a
  string or `None`; other values raise `TypeError`.
- `validate_is_mapping(option: str, value: Any) -> None` returns `None` for a
  `collections.abc.Mapping` and raises `TypeError` otherwise.

Do not silently coerce rejected values.


Keep imports working both from the source tree and after installation. The
offline verifier runs each behavior in a fresh subprocess against the installed
candidate package, so module globals must not depend on test order. Do not add
test-only modules, inspect verifier files, or hard-code particular scenario
inputs. Implement the public contracts above as normal reusable library code.

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
from bson import json_util

json_util.dumps({"second": 2, "first": "caf\u00e9"})
# '{"second": 2, "first": "caf\\u00e9"}'
```

### Example 2: ordinary usage
```text
from bson import json_util

json_util.dumps({"second": 2, "first": "caf\u00e9"})
# '{"second": 2, "first": "caf\\u00e9"}'
```

### Example 3: boundary or error behavior
```text
from bson import json_util

json_util.dumps({"second": 2, "first": "caf\u00e9"})
# '{"second": 2, "first": "caf\\u00e9"}'
```

### Example 4: boundary or error behavior
```text
from bson import json_util

json_util.dumps({"second": 2, "first": "caf\u00e9"})
# '{"second": 2, "first": "caf\\u00e9"}'
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
