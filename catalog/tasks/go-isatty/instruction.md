# Build a deterministic go-isatty terminal detector

## Project Description

Create the pure-Go package `github.com/mattn/go-isatty` at repository root.
It answers whether an operating-system file descriptor refers to a terminal and
exposes a separate check for Cygwin/MSYS2 terminals. The evaluator uses a
bounded JSON bridge so that ordinary files, pipes, `/dev/null`, and invalid
descriptors can be tested without requiring an interactive session.

## Supports

- Linux/amd64 with Go `1.26.5`, `CGO_ENABLED=0`, and one root `go.mod` whose
  module path is exactly `github.com/mattn/go-isatty`.
- Offline builds with `GOOS=linux GOARCH=amd64 GOWORK=off GOPROXY=off
  GOSUMDB=off GOTOOLCHAIN=local` and `-mod=vendor`.
- The declared dependency `golang.org/x/sys v0.28.0`, supplied by the build
  environment's pre-materialized module closure. Do not fetch dependencies at
  evaluation time.
- Pure Go calls that do not write to stdout, mutate global state, or require a
  network service. Keep OS-specific files correctly guarded by build tags.

## API Usage Guide

Implement package `isatty` at import path `github.com/mattn/go-isatty` with:

```go
func IsTerminal(fd uintptr) bool
func IsCygwinTerminal(fd uintptr) bool
```

`IsTerminal` accepts an OS file descriptor represented as `uintptr` and returns
true only when the descriptor is recognized as a terminal by the current
platform. On Linux, the frozen implementation uses the terminal window-size
ioctl (`TIOCGWINSZ`) through `golang.org/x/sys/unix`, rather than treating a
successful unrelated device ioctl as proof of a TTY. Invalid, closed, regular
file, pipe, and `/dev/null` descriptors return false and must not panic.

`IsCygwinTerminal` accepts the same descriptor and reports whether it is a
Cygwin/MSYS2 terminal. It returns false on Linux and on other platforms where
that terminal family is not supported. The function must be deterministic and
must not write diagnostics or change the descriptor.

Example:

```go
package main

import (
    "fmt"
    "os"

    "github.com/mattn/go-isatty"
)

func main() {
    fd := os.Stdout.Fd()
    fmt.Println(isatty.IsTerminal(fd), isatty.IsCygwinTerminal(fd))
}
```

The result for an actual interactive terminal depends on the host. The
contract does not require a pseudo-terminal to be created by the package.

## Implementation Notes

Keep the module self-contained apart from the declared `x/sys` dependency and
make calls safe for arbitrary `uintptr` values. Preserve the public import path
and both function signatures. Do not replace descriptor inspection with a
constant answer for `IsTerminal`, do not hard-code the bridge's fixture names,
and do not add a command-line-only facade. Unsupported platforms may use the
upstream platform-specific behavior and build tags, but the Linux build must
compile and run with cgo disabled.
