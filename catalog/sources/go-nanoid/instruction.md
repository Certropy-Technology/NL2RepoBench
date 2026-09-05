# Recreate go-nanoid/v2

## Project Description

Create a pure-Go module whose module path is exactly
`github.com/matoous/go-nanoid/v2`. It generates compact random IDs from a
caller-selected alphabet or from the package's URL-safe default alphabet. The
evaluator checks the observable root-package API through a typed subprocess
bridge; it does not require a command-line program.

## Natural Language Instruction

Create the module from an empty `workspace/` directory. Implement the exported
alphabet presets and the four generation functions in the API guide. Preserve
Unicode code-point counts, secure random generation, validation errors, and the
distinction between configurable exported variables and the fixed default
alphabet used by `New`. The package is a library, so no CLI, service, or
filesystem integration is required.

## Supports

- Linux/amd64 with Go `1.26.5`.
- A root `go.mod` with module path `github.com/matoous/go-nanoid/v2` and Go
  directive `1.26.5`, plus `go.sum` and `vendor/modules.txt`.
- Offline builds with `GOOS=linux`, `GOARCH=amd64`, `CGO_ENABLED=0`,
  `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`, and `GOTOOLCHAIN=local`.
- No third-party dependencies are needed by the package. Do not use cgo,
  plugins, external services, network access, or a Go workspace.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/
│   └── modules.txt
└── gonanoid.go
```

Import path: `github.com/matoous/go-nanoid/v2`. A caller imports it with
`import "github.com/matoous/go-nanoid/v2"`. The module root uses the
package name `gonanoid`. Keep the generated project limited to the
public module and its declared build metadata; do not add a command, service,
source checkout, or evaluator files.

## API Usage Guide

Implement package `gonanoid` at the module root with these public declarations:
Import example: `import gonanoid "github.com/matoous/go-nanoid/v2"`.

```go
var AlphaNum = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
var Alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
var AlphaLowerNum = "abcdefghijklmnopqrstuvwxyz0123456789"
var AlphaUpperNum = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
var AlphaLower = "abcdefghijklmnopqrstuvwxyz"
var AlphaUpper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
var Numeric = "0123456789"
var CrockfordBase32Upper = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
var CrockfordBase32Lower = "0123456789abcdefghjkmnpqrstvwxyz"

func Generate(alphabet string, size int) (string, error)
func MustGenerate(alphabet string, size int) string
func New(l ...int) (string, error)
func Must(l ...int) string
```

### `Generate` and `MustGenerate`

`Generate` returns an ID containing exactly `size` Unicode code points chosen
from `alphabet`, using a cryptographically strong random source. A non-empty
alphabet is required and its UTF-8 byte length must be at most 255. `size`
must be positive. The returned string may contain repeated characters and must
preserve the alphabet's Unicode code points, including multi-byte characters.
Invalid alphabet or size returns an empty string and a non-nil error. The
function must not mutate the caller's string. `MustGenerate` has the same
successful behavior and panics when `Generate` would return an error.

### `New` and `Must`

`New()` returns a 21-code-point ID using the default alphabet
`_-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`.
`New(n)` returns an ID of exactly `n` code points using that same alphabet;
`n == 0` is valid and returns an empty string, while a negative value returns
an error and an empty string. Passing more than one optional length is an
error. `Must` mirrors `New` and panics on invalid arguments. Every successful
non-zero ID must use only the default alphabet; successive calls should draw
fresh random bytes rather than reuse a fixed ID.

The exported alphabet variables above must be initialized to their documented
strings. They are variables, so ordinary Go callers may assign them; the
default alphabet used by `New` remains the package's private URL-safe default.

## Implementation Notes

Use rune-aware output sizing: `size` counts Unicode code points, while the
alphabet limit is measured in UTF-8 bytes as described above. Rejection
sampling may be used to avoid bias when an alphabet is not a power-of-two
length. Errors need only be non-nil and non-empty; callers must not depend on
their exact wording. Do not expose a deterministic seed or replace the secure
random source with a predictable generator.

## Examples

```go
package main

import (
    "fmt"
    gonanoid "github.com/matoous/go-nanoid/v2"
)

func main() {
    id, err := gonanoid.Generate(gonanoid.Numeric, 8)
    if err != nil {
        panic(err)
    }
    fmt.Println(id)
}
```

```go
id, err := gonanoid.Generate("猫犬", 2)
// id contains two runes and only characters from the supplied alphabet.
_ = id
_ = err
```

```go
empty, err := gonanoid.New(0)
// empty == "" and err == nil; a negative length returns an error.
_ = empty
_ = err
```

## Error Handling and Boundary Conditions

Reject an empty alphabet, an alphabet whose UTF-8 encoding exceeds 255 bytes,
and a non-positive custom generation size with a non-nil error and an empty
result. `New(0)` is the one valid zero-length case. A call to `Must` or
`MustGenerate` panics only when its corresponding fallible function would
return an error. Repeated successful calls must not return a fixed seeded
sequence, and output must remain within the selected alphabet.
