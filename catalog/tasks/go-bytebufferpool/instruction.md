# Build `go-bytebufferpool`

## Project Description

Create a pure-Go module that provides reusable byte buffers and a package-level
pool for reducing allocations. The repository must use module path
`github.com/valyala/bytebufferpool` and expose the root package
`bytebufferpool`.

The task covers deterministic buffer contents, byte counts, `io.ReaderFrom` and
`io.WriterTo` behavior, and the public pool lifecycle. Internal calibration
statistics and allocation optimizations are not directly observable and may be
implemented differently.

## Supports

- Linux/amd64 with Go 1.26.5.
- A single root `go.mod` and `go.sum`; build with `GOWORK=off`, `GOPROXY=off`,
  `GOSUMDB=off`, `GOTOOLCHAIN=local`, and `CGO_ENABLED=0`.
- Standard-library dependencies only. Do not use cgo, plugins, `unsafe`,
  `go:generate`, workspaces, external `replace` directives, network access, or
  external services.
- The zero value of `ByteBuffer` must be usable.

## API Usage Guide

Implement package `bytebufferpool` at import path
`github.com/valyala/bytebufferpool` with the following public API.

### `ByteBuffer`

```go
type ByteBuffer struct {
    B []byte
}

func (b *ByteBuffer) Len() int
func (b *ByteBuffer) ReadFrom(r io.Reader) (int64, error)
func (b *ByteBuffer) WriteTo(w io.Writer) (int64, error)
func (b *ByteBuffer) Bytes() []byte
func (b *ByteBuffer) Write(p []byte) (int, error)
func (b *ByteBuffer) WriteByte(c byte) error
func (b *ByteBuffer) WriteString(s string) (int, error)
func (b *ByteBuffer) Set(p []byte)
func (b *ByteBuffer) SetString(s string)
func (b *ByteBuffer) String() string
func (b *ByteBuffer) Reset()
```

`B` is the accumulated byte slice. `Len` returns its current byte length, not
the number of Unicode characters. `Bytes` returns the accumulated bytes in
their current order. `String` converts those bytes to a string without adding
or removing data.

`Write` appends every byte from `p` and returns `(len(p), nil)`. `WriteByte`
appends one byte and returns `nil`. `WriteString` appends the UTF-8 bytes of
the string and returns `(len(s), nil)`, where `len` is the Go byte length.
`Set` replaces the contents with a copy of `p`; later changes to the caller's
slice must not change the buffer. `SetString` replaces the contents with the
string's bytes. Both setters preserve usable capacity when possible. `Reset`
empties the buffer while leaving it usable for later writes.

`ReadFrom` appends all bytes read from `r` and returns the number of bytes read
by this call. A normal `io.EOF` after the final bytes is reported as `nil`.
Other reader errors are returned together with the bytes successfully read.
Existing contents remain before newly read contents. `WriteTo` writes the
current bytes once to `w` and returns the writer's byte count and error.

### Pools

```go
type Pool struct{}

func Get() *ByteBuffer
func Put(b *ByteBuffer)
func (p *Pool) Get() *ByteBuffer
func (p *Pool) Put(b *ByteBuffer)
```

`Get` and `Pool.Get` return a non-nil, empty `*ByteBuffer`. A buffer returned
by either getter can be filled using the methods above. `Put` and `Pool.Put`
return a buffer to the pool for reuse; callers must not access a buffer after
putting it. A later get must always return an empty buffer, regardless of the
contents previously put. Passing a nil buffer to `Put` is not part of the
contract and need not be supported.

The pool may discard unusually large buffers. Allocation reuse and the exact
capacity returned by `Get` are implementation details; tests must rely on
contents, lengths, and error behavior rather than a particular capacity.

## Implementation Notes

Keep the module self-contained and deterministic. The public methods must not
perform I/O except `ReadFrom` and `WriteTo` through the caller-provided
interfaces. Handle empty input, repeated reset/set/write operations, UTF-8
strings, short writes, and reader errors without panicking. Do not retain a
caller-owned slice after `Set` in a way that permits external mutation.

The evaluation invokes the public API through a bounded JSON subprocess bridge;
the trusted verifier does not import candidate code. The bridge groups
stateful buffer calls into a sequence and separately exercises reader, writer,
and pool behavior.
