# Build a deterministic data-selection library

## Project Description

Create the pure-Go module `github.com/tomwright/dasel/v3` and implement the
public library API used to query and modify JSON-shaped Go values. The task
focuses on deterministic selector evaluation, conversion to ordinary Go values,
and in-place updates. The command-line frontend, interactive terminal UI,
format readers/writers, file access, custom functions, and external services are
outside the task.

## Supports

- Linux/amd64 with Go `1.26.5`.
- A single root `go.mod` declaring module path `github.com/tomwright/dasel/v3`,
  Go `1.26.5`, the dependency closure needed by the package, and a matching
  `go.sum` plus `vendor/modules.txt` closure.
- Pure Go with `CGO_ENABLED=0`; build with
  `GOOS=linux GOARCH=amd64 GOWORK=off GOPROXY=off GOSUMDB=off
  GOTOOLCHAIN=local go build -mod=vendor ./...`.
- The evaluation process supplies JSON-compatible values only: `null`, booleans,
  strings, numbers, arrays, and objects with string keys. Do not require files,
  TTYs, callbacks, native objects, random state, clocks, network access, or
  external services.
- Selector and request inputs are bounded by the bridge: selectors are at most
  512 UTF-8 bytes, JSON requests are at most 128 KiB, and one request contains
  at most 64 array/object elements where the contract needs a bounded sequence.

## Natural Language Instruction

Build the pure-Go `github.com/tomwright/dasel/v3` module from an empty
workspace. Implement deterministic selector parsing, querying, conversion to
ordinary Go values, and in-place modification for JSON-shaped inputs as
specified below. CLI, file format, and interactive features are excluded.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
├── selector.go
├── value.go
└── modify.go
```

Keep package `dasel` at the root and its documented exported types/functions.
Do not include private verifier or hidden-test files.

## Examples

```go
value, err := New("{\"name\":\"Ada\"}", String).Select("name")
```

```go
updated, err := New("{\"count\":1}", JSON).Set("count", 2)
```

## Error Handling and Boundary Conditions

Handle malformed JSON, missing selectors, nulls, arrays, escaped names,
bounded selectors, and modification of absent paths according to the API guide.
Do not require files, TTYs, clocks, callbacks, or network access.

## API Usage Guide

Implement package `dasel` at import path `github.com/tomwright/dasel/v3` with:

```go
func Query(ctx context.Context, data any, selector string,
    opts ...execution.ExecuteOptionFn) ([]*model.Value, int, error)

func Select(ctx context.Context, data any, selector string,
    opts ...execution.ExecuteOptionFn) (any, int, error)

func Modify(ctx context.Context, data any, selector string, newValue any,
    opts ...execution.ExecuteOptionFn) (int, error)
```

### Query and Select

`Query` evaluates the selector against `data` and returns the selected values as
`*model.Value` objects, the number of selected values, and an error. A scalar
selection is one result; a branch or spread selection returns its elements in
selector order. `Select` has the same evaluation semantics, converts each
selected value with its `GoValue` representation, and returns a slice containing
the selected values plus the same count. Empty selections return an empty slice
and count zero. The `context.Context` must be honored for cancellation while
evaluating; normal bounded calls must not hang or panic.

Selectors used by this task include:

- `users.map(name)...` — map over an array and spread the selected field;
- `users.map(age >= 30 ? name : "junior")...` — comparisons and conditional
  expressions inside a map;
- `$this.map($this * 2)...` — map and arithmetic over a root array;
- `$this[1]` — index selection;
- `items.filter(active)...` — filter an array by a truthy field;
- `keys()...` — return object keys in the package's deterministic key order.

Property access, array indexes, map/spread, boolean and numeric literals,
comparison operators, arithmetic used in the examples, conditionals, and the
`$this` root variable are in scope. Results must preserve array order and JSON
scalar values. Map ordering must be deterministic for a repeated call; callers
must not rely on an order different from the package's documented behavior.

### Modify

`Modify` evaluates the selector against a pointer to a mutable JSON-compatible
value and replaces every selected value with `newValue`. It returns the number
of changed selections and an error. The update is in place: after a successful
call, the caller-visible pointed-to value contains the replacement while
unselected siblings remain unchanged. Examples include:

```go
data := any(map[string]any{
    "users": []any{
        map[string]any{"name": "Alice"},
        map[string]any{"name": "Bob"},
    },
})
count, err := dasel.Modify(ctx, &data, "users[1].name", "Robert")
// count == 1; data.users[1].name == "Robert"
```

An invalid selector or an incompatible selection returns a non-nil error and
must not corrupt unrelated data. A nil or non-pointer target is an error for
`Modify`. Do not mutate package-global state between calls.

## Implementation Notes

The evaluator invokes the package through a newline-delimited JSON bridge. The
bridge supports `query`, `select`, and `modify`; it decodes only JSON-compatible
values, emits one structured JSON response per request, and never prints
diagnostics to stdout. Candidate code is built and called in a separate
subprocess with no network. Keep the public module importable directly and do
not hard-code the private contract fixtures or expected responses.

The upstream repository contains many format adapters and a CLI. They are not
required for this bounded contract, but the root package and its selector/model
dependencies must compile under the stated offline vendor contract. Preserve
error returns, selector order, numeric/boolean/string values, and in-place
mutation semantics rather than returning a plausible constant response.
