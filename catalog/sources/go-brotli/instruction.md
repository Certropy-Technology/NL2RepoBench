# Build `github.com/andybalholm/brotli`

## Project Description

Create a pure-Go module whose root package is `github.com/andybalholm/brotli` and
whose subpackages are `github.com/andybalholm/brotli/flate` and
`github.com/andybalholm/brotli/matchfinder`. The module implements Brotli
compression/decompression, streaming writers/readers, DEFLATE/GZIP helpers, and
reusable LZ77 match-finding components.

## Supports

- Linux/amd64 with Go `1.26.5`, `CGO_ENABLED=0`, one root `go.mod`, and no Go
  workspace or external `replace` directive.
- Offline builds with `GOWORK=off GOPROXY=off GOSUMDB=off
  GOTOOLCHAIN=local` and `-mod=vendor`. Preserve the module path and the
  required `github.com/xyproto/randomstring v1.0.5` dependency in the locked
  vendor closure.
- Pure Go only. Do not use cgo, network services, plugins, generated source,
  or global state to answer bridge requests.
- The evaluator invokes a bounded line-oriented JSON subprocess. Keep stdout
  as JSON responses and write diagnostics to stderr.

## API Usage Guide

Root package `github.com/andybalholm/brotli`:

```go
func NewWriter(dst io.Writer) *Writer
func NewWriterLevel(dst io.Writer, level int) *Writer
func NewWriterOptions(dst io.Writer, options WriterOptions) *Writer
func NewWriterV2(dst io.Writer, level int) *matchfinder.Writer
func NewReader(src io.Reader) *Reader
func (w *Writer) Write(p []byte) (int, error)
func (w *Writer) Flush() error
func (w *Writer) Close() error
func (w *Writer) Reset(dst io.Writer)
func (r *Reader) Read(p []byte) (int, error)
func (r *Reader) Reset(src io.Reader) error
```

`NewWriterLevel` accepts Brotli qualities 0 through 11; `WriterOptions.Quality`
and `LGWin` select quality and sliding-window size. Writes may buffer input, so
call `Flush` or `Close`. `Reader` implements streaming `io.Reader` and returns
decoding errors for malformed or truncated streams. `Reset` reuses a reader or
writer with a new underlying stream and does not retain prior input.

The `flate` package provides `NewWriter`, `NewGZIPWriter`, `NewEncoder`, and
`NewGZIPEncoder`. Writer levels outside 1 through 9 are clamped to the nearest
supported level. Its writers use the `matchfinder` package and return standard
flate or gzip byte streams.

The `matchfinder` package provides `MatchFinder` and `Encoder` interfaces,
`Match{Unmatched, Length, Distance}`, `Writer`, `TextEncoder`, and the
`M0`, `M4`, `Pathfinder`, `Trio`, `Bargain1`, `Bargain2`, `Bargain3`, `ZFast`,
`ZDFast`, `ZM`, `NoMatchFinder`, and `AutoReset` implementations. A finder
appends deterministic LZ77 matches to the supplied destination and `Reset`
starts a new stream. `M0` rejects inputs longer than its documented 65536-byte
block limit; other configuration fields control match distance, hash table, or
chain search depth.

## Implementation Notes

Implement the public behavior rather than hard-coding evaluator fixtures.
Preserve byte-for-byte stream validity, round-trip decompression, streaming
boundaries, flush/close semantics, reset behavior, level handling, and the
matchfinder intermediate representation. The typed bridge is the adapter
boundary: callbacks, HTTP response writers, internal encoder state, and timing
benchmarks are outside the JSON contract. Do not write trusted reward or test
reports from candidate code.

