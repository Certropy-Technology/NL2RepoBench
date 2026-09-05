# Build the serializable Parse API of google/uuid

## Project Description

Create a pure-Go UUID parsing library. The repository must be a single Go
module whose module path is `github.com/google/uuid`. This task covers the
deterministic parsing and canonical string behavior of the package; random UUID
generation, database integration, and operating-system node discovery are out
of scope.

## Natural Language Instruction

Create the `github.com/google/uuid` module from an empty workspace. Implement
the serializable `UUID` value, all accepted parse spellings, canonical
lowercase formatting, and deterministic invalid-input errors described below.
Keep the implementation pure Go and limited to the public parse/string
contract; random generation and operating-system behavior are out of scope.

## Supports

- Linux/amd64 with Go 1.26.5.
- A root `go.mod` and `go.sum`; the module must build with `GOWORK=off`,
  `GOPROXY=off`, `GOSUMDB=off`, and `GOTOOLCHAIN=local`.
- One pure-Go module only. Do not use cgo, plugins, `unsafe`, `go generate`, a
  workspace, an external `replace` directive, network access, or external
  services.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
└── uuid.go
```

The module root is imported as `github.com/google/uuid` and its public package
name is `uuid`. Keep the implementation self-contained and independent of
evaluator-only files.

## API Usage Guide

Implement package `uuid` at import path `github.com/google/uuid` with:

```go
import uuid "github.com/google/uuid"

type UUID [16]byte

func Parse(value string) (UUID, error)

func (value UUID) String() string
```

`Parse` accepts hexadecimal digits case-insensitively in these forms:

- canonical: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- compact: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- URN: `urn:uuid:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`, with a
  case-insensitive `urn:uuid:` prefix
- brace-delimited: `{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}`

For every accepted form, `String` returns the same 16-byte UUID in lowercase
canonical form. Invalid lengths, non-hexadecimal digits, misplaced canonical
hyphens, and an invalid URN prefix return a non-nil error and do not panic.

Example:

```go
id, err := Parse("URN:UUID:550E8400-E29B-41D4-A716-446655440000")
if err != nil {
    // handle invalid input
}
fmt.Println(id.String())
// 550e8400-e29b-41d4-a716-446655440000
```

The compact spelling is also accepted and produces the same canonical value:

```go
id, err := uuid.Parse("550e8400e29b41d4a716446655440000")
if err == nil {
    fmt.Println(id.String())
}
```

`UUID` is a value type: copying it copies all sixteen octets, equality compares
the octets, and formatting never depends on locale, time, or process state.
`Parse` must decode each hexadecimal pair in network order. A successful parse
must not retain a reference to the input string, and an error result must be
safe to inspect without exposing partially decoded bytes.

The canonical formatter always emits four hyphen-separated groups of lengths
8, 4, 4, and 4 followed by 12 hexadecimal digits. It uses lowercase digits
even when the input used uppercase digits, braces, a compact spelling, or an
uppercase URN prefix.

## Examples

```go
var zero uuid.UUID
fmt.Println(zero.String())
// 00000000-0000-0000-0000-000000000000
```

```go
_, err := uuid.Parse("not-a-uuid")
if err == nil {
    panic("invalid input must return an error")
}
```

## Error Handling and Boundary Conditions

Return a non-nil error for wrong length, non-hexadecimal characters,
misplaced hyphens, and an invalid `urn:uuid:` prefix. Invalid input must not
panic. Parsing is deterministic and does not mutate package-global state.

Do not accept extra whitespace, an extra brace, a fifth canonical hyphen, or
trailing characters after a valid UUID. The zero value and every successfully
parsed value must be safe to call from multiple goroutines because the value
methods do not mutate shared state.

## Implementation Notes

The zero value of `UUID` must be usable and stringify as
`00000000-0000-0000-0000-000000000000`. Parsing must be deterministic and
must not retain references to input storage or mutate global state.
