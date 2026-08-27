# Build a bounded GJSON query library

## Project Description

Create the pure-Go `github.com/tidwall/gjson` package at repository root. It
parses JSON text and retrieves values using GJSON paths. The task exercises the
library's deterministic string-input query, result conversion, validation, and
path escaping behavior. Runtime registration of custom modifiers, byte-slice
zero-copy behavior, iterator APIs, and benchmark code are outside this task.

## Supports

- Linux/amd64 with Go `1.26.5`.
- Exactly one root `go.mod` module with module path
  `github.com/tidwall/gjson`, a matching `go.sum`, and no workspace or
  external `replace` directive.
- Pure Go with `CGO_ENABLED=0`; do not use cgo, plugins, generated code, or
  network services. The repository must build and run with
  `GOOS=linux GOARCH=amd64 GOWORK=off GOPROXY=off GOSUMDB=off
  GOTOOLCHAIN=local`.
- The two declared Go module dependencies must be available from the module
  closure and the package must build with `-mod=vendor` while offline.

## API Usage Guide

Implement package `gjson` and preserve these public contracts.

### JSON parsing and querying

```go
func Parse(json string) Result
func Get(json, path string) Result
func GetMany(json string, path ...string) []Result
func Valid(json string) bool
func Escape(component string) string
```

`Parse` returns the first JSON value in the input, preserving its raw JSON
representation. `Get` searches an object or array using a dot-separated path
and returns a zero/non-existent `Result` when the path is absent. `GetMany`
returns one result per requested path, in the same order as the paths. `Valid`
reports whether the complete input is valid JSON. `Escape` escapes dots and
the wildcard characters in one path component so that it can be used as a
literal key.

The supported path subset must include object keys, decimal array indexes,
`#` array counts, `*` and `?` key wildcards, escaped dots and wildcards, and
array queries using the comparison operators `==`, `!=`, `<`, `<=`, `>`, `>=`
and the pattern operators `%` and `!%`. The typed bridge rejects a path longer
than 256 bytes, a path with more than 16 dot-separated components, or a
`get_many` request with more than 32 paths. Inputs outside these bounds must
not reach the package or allocate without bound.

Paths are deterministic: repeated calls with the same JSON and path return
the same result and do not mutate global state. Whitespace around a JSON
value is accepted. Invalid JSON is not required to be rejected by `Parse` or
`Get`, but those functions must not panic.

### Result values

`Result` is a public struct with fields `Type`, `Raw`, `Str`, `Num`, `Index`,
and `Indexes`. Define the public `Type` constants `Null`, `False`, `Number`,
`String`, `True`, and `JSON`. `Type.String()` returns exactly the matching
capitalized name (`Null`, `False`, `Number`, `String`, `True`, or `JSON`), and
returns an empty string for an unknown value.

The following methods must be available with these signatures:

```go
func (r Result) String() string
func (r Result) Bool() bool
func (r Result) Int() int64
func (r Result) Uint() uint64
func (r Result) Float() float64
func (r Result) Exists() bool
func (r Result) IsObject() bool
func (r Result) IsArray() bool
func (r Result) IsBool() bool
func (r Result) Array() []Result
func (r Result) Map() map[string]Result
func (r Result) Get(path string) Result
```

`Result.String` returns the decoded string for a JSON string, the original
number spelling when it is an integer, raw JSON for objects and arrays, and
`true`/`false` for booleans. `Bool`, `Int`, `Uint`, and `Float` convert the
result using the natural JSON scalar conversion; absent, null, and unrelated
types return their zero values. `Exists` is false only for an absent result.
The type predicates identify the JSON value kind. `Array` returns the members
of an array, an empty slice for absent/null, or a one-element slice for a
scalar. `Map` returns object members and an empty map for non-objects. `Get`
queries within the current result using the same bounded path rules.

### Typed bridge behavior

The evaluator invokes the package through newline-delimited JSON on a small
subprocess bridge. The bridge accepts operations `get`, `parse`, `valid`,
`get_many`, and `escape`, each with JSON arguments, and emits one JSON response
per request. For `get` and `parse`, serialize the selected `Result` fields and
the scalar methods described above. Error responses must be structured JSON;
the bridge must never print diagnostics to stdout or panic on malformed input.

## Implementation Notes

Keep the public package importable directly as `github.com/tidwall/gjson`.
The repository is evaluated from an empty workspace, so include all source,
module metadata, and the offline vendor closure needed to build it. Preserve
JSON string escapes, Unicode, large integer spellings, duplicate object-key
lookup behavior, and array/object ordering. Do not expose hidden fixtures or
hard-code evaluator examples in the public bridge.
