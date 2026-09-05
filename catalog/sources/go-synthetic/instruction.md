# Build a pure-Go text utility

## Project Description

Create a minimal installable Go module for callers that need one deterministic
text-normalization helper. The project accepts a string and returns a string;
it has no persistence, command-line service, network, or third-party runtime.
The task is intentionally small, but the repository must still be a complete
module that can be built from an empty workspace.

## Natural Language Instruction

Create the single module `example.com/go-synthetic` with a public package
`textx`. Implement the exported `Normalize(value string) string` function.
Remove only surrounding ASCII whitespace (`' '`, `\t`, `\n`, `\r`, `\f`, and
`\v`) and preserve every other byte and rune in its original order. Keep the
function deterministic and side-effect free.

The package must be usable through a bounded typed JSON subprocess bridge. The
bridge is an evaluation boundary, not part of the project to be created: the
implementation should expose the Go package and must not assume that callers
can share Go pointers or process state.

## Supports

- Go on Linux/amd64 with `CGO_ENABLED=0`.
- A single root module whose path is exactly `example.com/go-synthetic`.
- A root `go.mod` with package source under `textx/` and no `replace`
  directives, workspace file, or external dependency.
- Offline build and test commands with `GOWORK=off`, `GOPROXY=off`,
  `GOSUMDB=off`, and `GOTOOLCHAIN=local`.
- Standard-library-free implementation is preferred; the function can be
  implemented with direct byte/rune checks and must not require a service.
- No cgo, plugins, generated source, subprocesses, files, clocks, randomness,
  global mutable state, or environment-dependent behavior.

## Project Directory Structure

```text
workspace/
├── go.mod
└── textx/
    └── textx.go
```

`go.mod` declares `module example.com/go-synthetic`. The file
`textx/textx.go` declares `package textx` and the public function at the import
path `example.com/go-synthetic/textx`. No command, data directory, or runtime
configuration is needed.

## API Usage Guide

### `example.com/go-synthetic/textx.Normalize`

```go
func Normalize(value string) string
```

`value` may be empty or any UTF-8/byte string. The function returns a new string
value with a maximal run of the six ASCII whitespace bytes removed from the
left and right edges. It does not trim internal whitespace, Unicode whitespace,
punctuation, or non-ASCII bytes. The return type is always `string`; there is
no error result and no mutation of caller-owned storage.

The operation is idempotent: normalizing an already normalized value returns
the same value. A nil concept does not apply to a Go string. Invalid UTF-8 is
still ordinary string data and must be preserved except for matching ASCII
edge bytes.

## Implementation Notes

Keep the module path, package name, and function signature exact. Do not add a
second package at the module root or a competing `Normalize` symbol. Avoid
locale-aware trimming because the contract is explicitly ASCII-only. The same
input must always produce the same output, and the implementation must not log,
write files, inspect the network, or retain process-global state.

The package should compile with the standard offline Go toolchain and should
not depend on the current working directory. A caller can invoke the function
repeatedly and concurrently because it has no mutable package configuration.

## Examples

```go
package main

import (
    "fmt"
    "example.com/go-synthetic/textx"
)

func main() {
    fmt.Println(textx.Normalize("  hello  ")) // hello
}
```

```go
textx.Normalize("\tleft and right\n") // "left and right"
textx.Normalize("left  middle  right") // "left  middle  right"
```

## Error Handling and Boundary Conditions

The function has no error return. Empty input returns empty output. Input made
entirely from ASCII whitespace returns empty output. Leading/trailing tabs,
line feeds, carriage returns, form feeds, and vertical tabs are removed; any
other edge byte, including a non-breaking space or another Unicode whitespace
rune encoded in UTF-8, is not removed by this contract.

```go
textx.Normalize("  a  b  ")       // "a  b"
textx.Normalize("\u00a0value\u00a0") // unchanged non-ASCII edges
textx.Normalize("x\n\ty")          // internal whitespace remains
```

Malformed JSON or an unsupported bridge request is the bridge caller's error;
the package function itself must not panic for any string value. Diagnostics,
if a surrounding program has them, belong outside the function's return value
and must never alter normalization results.
The module's public surface is intentionally limited to this one package and
function. A normal `go test` or `go build` from the workspace root works
without fetching modules or depending on files outside the workspace.
