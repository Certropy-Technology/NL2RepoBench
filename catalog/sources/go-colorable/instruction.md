# Implement a deterministic ANSI writer package

## Project Description

Create the pure-Go module `github.com/mattn/go-colorable` at the repository
root. It provides `io.Writer` adapters for terminal output: the Unix adapter
passes terminal output through, while the non-colorable adapter removes ANSI
escape sequences before writing to an underlying writer.

The evaluator uses Linux/amd64 behavior only. The package must build as a
normal Go module and must not require a network service, cgo, generated code,
or mutable global state.

## Supports

- Go `1.26.5`, Linux/amd64, `CGO_ENABLED=0`, and exactly one root `go.mod`.
- Module path `github.com/mattn/go-colorable`.
- Offline compilation with `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
  `GOTOOLCHAIN=local`, and `-mod=vendor`.
- The public package at the module root. Keep the package importable as
  `github.com/mattn/go-colorable`.
- Standard-library `io`, `os`, and `bytes` are sufficient for the evaluated
  Linux behavior. Do not add a runtime service or a CLI entry point.

## API Usage Guide

### `NewNonColorable`

Import `github.com/mattn/go-colorable` and use:

```go
func NewNonColorable(w io.Writer) io.Writer
```

The returned writer forwards ordinary bytes to `w` while removing terminal
escape sequences. It must accept arbitrary bytes, not only valid UTF-8. Every
ordinary byte, including NUL and non-UTF-8 bytes, is preserved in order.

CSI sequences begin with ESC followed by `[`. For a CSI sequence, consume the
sequence through its final ASCII letter or `@` byte and write none of those
control bytes. This includes common color, erase, cursor, and reset sequences.
An ESC byte that is not followed by `[` is also control input and must not be
written; the byte immediately following that ESC is part of the same ignored
escape pair. An incomplete escape at the end is ignored. Text after an escape
sequence is still forwarded.

`Write` returns the number of input bytes accepted, which is the length of the
provided byte slice for the normal in-memory writer case, and returns a nil
error. A write does not retain parser state between calls: each call is
interpreted independently.

The exported `NonColorable` type implements `io.Writer`; its observable
behavior is the same as the value returned by `NewNonColorable`.

Example:

```go
var out bytes.Buffer
w := colorable.NewNonColorable(&out)
_, _ = w.Write([]byte("info: \x1b[32mok\x1b[0m"))
// out.String() == "info: ok"
```

### Unix constructors

On Linux, these functions expose ordinary `*os.File` writers:

```go
func NewColorable(file *os.File) io.Writer
func NewColorableStdout() io.Writer
func NewColorableStderr() io.Writer
```

`NewColorable` returns the supplied file itself, so bytes including ANSI
sequences pass through unchanged. Passing `nil` to `NewColorable` panics.
The stdout and stderr constructors return the process `os.Stdout` and
`os.Stderr` files respectively.

### `EnableColorsStdout`

On Linux use:

```go
func EnableColorsStdout(enabled *bool) func()
```

If `enabled` is non-nil, set it to `true` and return a no-op cleanup function.
If it is nil, return the cleanup function without panicking. Calling the
cleanup function does not undo the change on Linux.

## Implementation Notes

Use build constraints only when needed for the Linux target. Keep the writer
boundary based on `io.Writer`, preserve input byte counts, and propagate a
deterministic result for repeated calls. The evaluator calls the public API
through a separate typed subprocess bridge using bounded JSON values; it does
not import candidate code into the trusted verifier. Do not hard-code the
evaluator's private request cases or write verifier reports, rewards, or test
results from candidate code.
