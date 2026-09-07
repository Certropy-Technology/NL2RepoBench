# Build the serializable Parse API of `google/uuid`

## Project Description

Create a pure-Go UUID package in a single module. The package must expose the
public import path `github.com/google/uuid` and represent a UUID as 16 bytes.
This task evaluates deterministic parsing and canonical text formatting. Random
UUID generation, time-based generation, node discovery, SQL integration, JSON
marshalling, and mutable package configuration are outside the requested
contract.

## Natural Language Instruction

Build the module from an empty `workspace/`. Implement the serializable
`UUID` value, strict `Parse` spellings, and lowercase canonical `String` output
described in the API guide. Keep the package deterministic and self-contained;
do not broaden the task into random generation, database integration, or a
network service.

## Supports

- Linux/amd64 with Go 1.26.5.
- A root `go.mod` whose module path is exactly `github.com/google/uuid` and
  whose `go` directive is exactly `1.26.5`.
- A root `go.sum` file, which may be empty because this task has no external
  dependencies.
- Build and test operation with `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
  and `GOTOOLCHAIN=local`.
- One pure-Go module. Do not require cgo, plugins, unsafe code, generated
  sources, network access, or external services.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
└── uuid.go
```

The module path is `github.com/google/uuid`, and the root package name is
`uuid`. The root source file must expose the documented `UUID` type and
methods. No CLI, generated test package, service, or external module is
needed.

## API Usage Guide

Implement package `uuid` at import path `github.com/google/uuid` with this
exported type and methods:

```go
type UUID [16]byte

func Parse(s string) (UUID, error)

func (uuid UUID) String() string
```

`Parse` returns the 16 bytes represented by hexadecimal digits, accepting these
four exact shapes:

- canonical: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- compact: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- URN: `urn:uuid:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- brace-delimited: `{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}`

The hexadecimal digits are case-insensitive. The URN prefix is also
case-insensitive, but it must be exactly nine characters (`urn:uuid:`) before
the canonical UUID. A brace-delimited value must have both the opening `{` and
closing `}`. Canonical hyphens must occur at offsets 8, 13, 18, and 23 after
removing an optional URN prefix or braces. Do not trim whitespace or accept
other separators, lengths, prefixes, or wrappers.

On success, `Parse` returns the same byte sequence for all accepted spellings.
On failure it returns a non-nil error and must not panic. The exact error text
is not part of this task's contract, but length errors, malformed separators,
invalid hexadecimal digits, invalid URN prefixes, and unmatched braces must be
distinguishable from success.

`String` has no side effects and always returns the lowercase canonical
36-character form with hyphens. The zero value is valid and must stringify as
`00000000-0000-0000-0000-000000000000`.

Example:

```go
id, err := uuid.Parse("URN:UUID:550E8400-E29B-41D4-A716-446655440000")
if err != nil {
    // handle invalid input
}
fmt.Println(id.String())
// 550e8400-e29b-41d4-a716-446655440000
```

## Implementation Notes

Keep the module self-contained and deterministic. Parsing must copy decoded
bytes into the returned `UUID`; it must not retain input storage or mutate
global state. Any additional exported API is optional, but the required API
above must remain available at the stated import path and must compile with
the offline commands in this specification.

## Examples

```go
package main

import (
    "fmt"
    "github.com/google/uuid"
)

func main() {
    id, err := uuid.Parse("550e8400-e29b-41d4-a716-446655440000")
    if err != nil {
        panic(err)
    }
    fmt.Println(id.String())
}
```

```go
zero := uuid.UUID{}
// zero.String() is the lowercase all-zero canonical UUID.
_ = zero
```

```go
id, err := uuid.Parse("550e8400e29b41d4a716446655440000")
// Compact and canonical spellings produce the same UUID bytes.
_ = id
_ = err
```

## Error Handling and Boundary Conditions

Parsing must fail without panicking for invalid lengths, malformed hyphen
positions, non-hexadecimal characters, invalid URN prefixes, unmatched braces,
and leading or trailing whitespace. Do not trim or normalize unsupported input.
`String` must remain total for the zero value and always return exactly 36
lowercase hexadecimal characters with four hyphens.
