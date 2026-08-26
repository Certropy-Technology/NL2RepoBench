# Build the serializable Parse API of google/uuid

## Project Description

Create a pure-Go UUID parsing library. The repository must be a single Go
module whose module path is `github.com/google/uuid`. This task covers the
deterministic parsing and canonical string behavior of the package; random UUID
generation, database integration, and operating-system node discovery are out
of scope.

## Supports

- Linux/amd64 with Go 1.26.5.
- A root `go.mod` and `go.sum`; the module must build with `GOWORK=off`,
  `GOPROXY=off`, `GOSUMDB=off`, and `GOTOOLCHAIN=local`.
- One pure-Go module only. Do not use cgo, plugins, `unsafe`, `go generate`, a
  workspace, an external `replace` directive, network access, or external
  services.

## API Usage Guide

Implement package `uuid` at import path `github.com/google/uuid` with:

```go
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

## Implementation Notes

The zero value of `UUID` must be usable and stringify as
`00000000-0000-0000-0000-000000000000`. Parsing must be deterministic and
must not retain references to input storage or mutate global state.
