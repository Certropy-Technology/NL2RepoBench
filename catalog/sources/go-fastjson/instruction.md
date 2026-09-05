# Build a bounded fastjson package

## Project Description

Create the pure-Go `github.com/valyala/fastjson` package at repository root.
The package parses, validates, scans, queries, mutates, and constructs JSON
without decoding into `interface{}` trees. The evaluator exercises a bounded,
serializable root-package API through a typed subprocess bridge. The internal
`fastfloat` subpackage, benchmark helpers, go-fuzz entrypoints, zero-copy byte
aliasing, and concurrent use of a single parser, scanner, arena, object, or
value are outside this task.

## Natural Language Instruction

Create an installable Go module from an empty `workspace/` using the module
path and package name documented below. Implement the public `fastjson` parser,
value accessors, object and array mutation helpers, scanner, and arena APIs.
Preserve Go signatures, nil behavior, error values, numeric and string
decoding, insertion order where documented, and deterministic JSON output.
The package is evaluated in a local child process and must not require a live
service, filesystem fixture, or network access.

## Supports

- Linux/amd64 with Go `1.26.5` and `CGO_ENABLED=0`.
- Exactly one root `go.mod` with module path
  `github.com/valyala/fastjson`, a matching `go.sum`, and no Go workspace,
  toolchain directive, or `replace` directive.
- No third-party modules. Include an empty `vendor/modules.txt` so the package
  builds with `-mod=vendor` while `GOWORK=off GOPROXY=off GOSUMDB=off
  GOTOOLCHAIN=local`.
- Deterministic in-memory behavior only. Do not use cgo, plugins, generated
  code, files, clocks, randomness, network services, or subprocesses.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/
│   └── modules.txt
├── parser.go
├── scanner.go
├── arena.go
├── value.go
└── fastfloat/
    └── fastfloat.go
```

The root files implement package `fastjson`; the optional internal
`fastfloat` directory is not a required import path for callers. Keep package
tests and verifier bridges out of the generated submission.

## API Usage Guide

Import path: `github.com/valyala/fastjson`. The following signatures are
available from the root `fastjson` package; no subpackage import is needed for
the scored contract.

```go
import "github.com/valyala/fastjson"

var p fastjson.Parser
value, err := p.Parse(`{"ok":true}`)
```

Implement package `fastjson` and preserve the following public contracts.

### Parsing and validation

```go
const MaxDepth = 300

func Parse(s string) (*Value, error)
func ParseBytes(b []byte) (*Value, error)
func MustParse(s string) *Value
func MustParseBytes(b []byte) *Value
func Validate(s string) error
func ValidateBytes(b []byte) error

type Parser struct { /* private state */ }
func (p *Parser) Parse(s string) (*Value, error)
func (p *Parser) ParseBytes(b []byte) (*Value, error)

type ParserPool struct { /* private state */ }
func (pp *ParserPool) Get() *Parser
func (pp *ParserPool) Put(p *Parser)
```

Parsing accepts leading and trailing JSON whitespace and requires exactly one
complete value. It supports objects, arrays, strings with JSON escapes,
numbers, booleans, and null. In addition to strict JSON numbers, the parser's
documented best-effort number grammar accepts spellings such as `.2`, `+1`,
and case-insensitive `NaN` or signed `Inf`; these are returned as
`TypeNumber`. `Validate` and `ValidateBytes` remain strict JSON validators and
reject those extensions. Other invalid syntax, trailing non-whitespace data,
and nested input deeper than `MaxDepth` return an error. The `MustParse`
variants panic on parse errors. A `Parser` is reusable, but a returned `Value`
and all children derived from it remain valid only until that parser's next
parse. Putting a parser into `ParserPool` invalidates values obtained from it.

### Types and values

```go
type Type int

const (
    TypeNull Type = iota
    TypeObject
    TypeArray
    TypeString
    TypeNumber
    TypeTrue
    TypeFalse
)

func (t Type) String() string

type Value struct { /* private state */ }
func (v *Value) Type() Type
func (v *Value) String() string
func (v *Value) StringBytes() ([]byte, error)
func (v *Value) Bool() (bool, error)
func (v *Value) Int() (int, error)
func (v *Value) Int64() (int64, error)
func (v *Value) Uint() (uint, error)
func (v *Value) Uint64() (uint64, error)
func (v *Value) Float64() (float64, error)
func (v *Value) Object() (*Object, error)
func (v *Value) Array() ([]*Value, error)
func (v *Value) MarshalTo(dst []byte) []byte
```

`Type.String` returns `null`, `object`, `array`, `string`, `number`, `true`, or
`false` for the matching constant and panics for an unknown `Type`. Typed
accessors return the underlying value only for a compatible JSON type and
return an error otherwise. `MarshalTo` appends the package's compact value
spelling to `dst`, preserving object entry order and permissive number
spellings. JSON string accessors return decoded string content.

### Lookup helpers

```go
func Exists(data []byte, keys ...string) bool
func GetString(data []byte, keys ...string) string
func GetBytes(data []byte, keys ...string) []byte
func GetInt(data []byte, keys ...string) int
func GetFloat64(data []byte, keys ...string) float64
func GetBool(data []byte, keys ...string) bool

func (v *Value) Get(keys ...string) *Value
func (v *Value) Exists(keys ...string) bool
func (v *Value) GetStringBytes(keys ...string) []byte
func (v *Value) GetInt(keys ...string) int
func (v *Value) GetInt64(keys ...string) int64
func (v *Value) GetUint(keys ...string) uint
func (v *Value) GetUint64(keys ...string) uint64
func (v *Value) GetFloat64(keys ...string) float64
func (v *Value) GetBool(keys ...string) bool
func (v *Value) GetObject(keys ...string) *Object
func (v *Value) GetArray(keys ...string) []*Value
```

Each key selects an object member. For arrays, a key containing a non-negative
decimal index selects that element. Missing paths, invalid indexes, malformed
JSON in the package-level helpers, or incompatible types return the documented
zero value: `nil`, `false`, `0`, or an empty string. `GetBytes` returns a copy
that remains valid after the helper returns.

### Objects, arrays, and mutation

```go
type Object struct { /* private state */ }
func (o *Object) Get(key string) *Value
func (o *Object) Len() int
func (o *Object) Visit(f func(key []byte, v *Value))
func (o *Object) Set(key string, value *Value)
func (o *Object) Del(key string)
func (o *Object) MarshalTo(dst []byte) []byte
func (o *Object) String() string

func (v *Value) Set(key string, value *Value)
func (v *Value) SetArrayItem(idx int, value *Value)
func (v *Value) Del(key string)
```

Objects preserve parsed and insertion order. `Set` replaces an existing key in
place or appends a new key. Passing a nil value stores JSON null. Object `Del`
removes the matching key. On an array, `Set` accepts a non-negative decimal
index and delegates to `SetArrayItem`; `SetArrayItem` requires `idx >= 0`, and
extending beyond the current length fills gaps with null. Array `Del` removes
the indexed element and shifts later elements. A malformed index passed to
`Set` or `Del`, a missing key, a nil receiver, or an operation on the wrong
container type is a no-op. The typed bridge rejects a negative direct
`SetArrayItem` index before calling the package.

### Scanning and arena construction

```go
type Scanner struct { /* private state */ }
func (sc *Scanner) Init(s string)
func (sc *Scanner) InitBytes(b []byte)
func (sc *Scanner) Next() bool
func (sc *Scanner) Value() *Value
func (sc *Scanner) Error() error

type Arena struct { /* private state */ }
func (a *Arena) NewObject() *Value
func (a *Arena) NewArray() *Value
func (a *Arena) NewString(s string) *Value
func (a *Arena) NewStringBytes(b []byte) *Value
func (a *Arena) NewNumberFloat64(f float64) *Value
func (a *Arena) NewNumberInt(n int) *Value
func (a *Arena) NewNumberString(s string) *Value
func (a *Arena) NewNull() *Value
func (a *Arena) NewTrue() *Value
func (a *Arena) NewFalse() *Value
func (a *Arena) Reset()

type ArenaPool struct { /* private state */ }
func (ap *ArenaPool) Get() *Arena
func (ap *ArenaPool) Put(a *Arena)
```

`Scanner` reads consecutive whitespace-delimited JSON values. `Next` returns
false at clean end-of-input with `Error() == nil`; malformed input produces a
non-nil error. The current value remains valid only until the next `Next`.
Arena-created values remain valid until `Reset` or until the arena is put back
in a pool. `Reset` must clear all cached value, object, array, and string state
before the arena is reused. `NewNumberString` stores the supplied spelling
without validation; callers are responsible for supplying a number spelling
appropriate for their output. The typed bridge accepts only strict JSON number
spellings for arena construction.

### Typed bridge behavior

The evaluator compiles a small bridge against the package and exchanges
newline-delimited JSON. It uses operations `parse`, `validate`, `get`, `handy`,
`scan`, `mutate`, `arena_build`, `arena_reset`, and `pool_parse`. Responses are
structured JSON and preserve JSON types, compact marshaled form, object order,
and applicable scalar conversions. A parsed `NaN` or infinity remains visible
through its type and marshaled spelling, while its non-JSON float conversion
is omitted from the response. The bridge limits a request line to 256 KiB,
JSON text to 128 KiB, paths to 16 components, streams and parser-pool
batches to 64 values, mutations to 64 steps, and recursive snapshots/builds to
32 levels and 2048 nodes. Inputs outside these bounds return `InvalidInput`.
Malformed JSON called through package APIs returns `CallFailed`. The bridge
must never print diagnostics to stdout or panic on malformed requests.

## Implementation Notes

Keep the public package importable directly as
`github.com/valyala/fastjson`. Preserve numeric spelling when marshaling parsed
values, JSON escape semantics, duplicate object entries and visit order, null
gap filling, parser/scanner lifetime rules, and arena cache reset behavior.
The evaluator starts from an empty workspace, so include all source, module
metadata, and the empty offline vendor closure. Do not hard-code bridge
examples or expose hidden fixtures.

## Examples

```go
var parser fastjson.Parser
value, err := parser.Parse(`{"items":[1,true,null]}`)
if err != nil {
    panic(err)
}
_ = value.GetArray()
```

```go
var arena fastjson.Arena
value := arena.NewObject().Set("ok", arena.NewTrue())
encoded := value.MarshalTo(nil)
```

```go
var scanner fastjson.Scanner
scanner.Init(`1 {"ok":true}`)
for scanner.Next() {
    _ = scanner.Value()
}
```

## Error Handling and Boundary Conditions

Malformed JSON returns the package's documented parse error rather than a
panic. Nil pointers and unavailable object or array paths return the documented
zero or false result. Parser, scanner, arena, object, and value instances are
not safe for concurrent use unless the caller provides synchronization. Reset
an arena only after its values are no longer used; scanner values are valid
only until the next scan. Inputs beyond the documented bridge bounds are
rejected before they can allocate unbounded state.
