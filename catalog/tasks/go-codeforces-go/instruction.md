# Build the `copypasta` Bitset package

## Project Description

Create a Go module with module path `github.com/EndlessCheng/codeforces-go`.
Implement the exported `Bitset` data structure in package
`github.com/EndlessCheng/codeforces-go/copypasta`. This is a bounded,
in-memory bit set for deterministic integer-indexed operations. It has no
network, filesystem, cgo, generated-code, or third-party dependency behavior.

The evaluator uses Linux/amd64, where a `uint` word has 64 bits. It invokes the
package through a newline-delimited JSON bridge. The bridge only supplies
non-negative indexes and half-open ranges wholly inside the allocated bitset.

## Natural Language Instruction

Create the offline Go module from an empty workspace and implement the mutable
`copypasta.Bitset` type with the complete point, search, range, shift,
arithmetic, and relation API below. Preserve 64-bit word behavior on the target
platform, inclusive search semantics, capacity sentinels, and deterministic
JSON bridge responses. The public module and package import paths are part of
the contract; do not add unrelated packages or services.

## Supports

- Go `1.26.5`, Linux/amd64, `CGO_ENABLED=0`.
- A root `go.mod` declaring exactly `module github.com/EndlessCheng/codeforces-go`
  and `go 1.26.5`, plus a `go.sum` and an offline `vendor/` directory.
- Offline builds with `GOWORK=off GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local`
  and `go build -mod=vendor`.
- Standard library imports only. Do not add a workspace, `replace` directive,
  plugins, cgo, external commands, or background work.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/
│   └── modules.txt
└── copypasta/
    └── bitset.go
```

The module path is `github.com/EndlessCheng/codeforces-go`; consumers import
`github.com/EndlessCheng/codeforces-go/copypasta`. The source tree contains no
verifier, bridge, generated artifact, or network-dependent package. The bridge
used for evaluation is external to this public module.

## API Usage Guide

Import the type with
`import "github.com/EndlessCheng/codeforces-go/copypasta"`. Put the
implementation in package `copypasta` at `copypasta/`. Define:

```go
func NewBitset(n int) Bitset
type Bitset []uint
```

`NewBitset(n)` allocates enough machine words to represent positions
`[0, n)`: `(n + 63) / 64` words on the target platform. `Bitset` is mutable;
methods with a `Bitset` receiver update that slice in place. The bridge uses
bitsets whose allocation is an exact number of 64-bit words.

Implement the following point operations for valid positions:

```go
func (b Bitset) Has(p int) bool
func (b Bitset) Set(p int)
func (b Bitset) Reset(p int)
func (b Bitset) Flip(p int)
```

`Has` reports the bit, `Set` makes it one, `Reset` makes it zero, and `Flip`
toggles it. A repeated `Set` or `Reset` is idempotent.

Implement these search and summary operations:

```go
func (b Bitset) Index0() int
func (b Bitset) Index1() int
func (b Bitset) Next0(p int) int
func (b Bitset) Next1(p int) int
func (b Bitset) LastIndex1() int
func (b Bitset) OnesCount() int
func (b Bitset) OnesCountRange(l, r int) int
func (b Bitset) TrailingZeros() int
func (b Bitset) Len() int
func (b Bitset) AllIndex1() []int
func (b Bitset) String() string
```

`Index0` and `Index1` return the first clear or set bit respectively. If none
exists, `Index1` returns the bitset capacity and `Index0` returns its capacity.
`Next0(p)` and `Next1(p)` search inclusively from `p` and use that same capacity
sentinel if no matching bit exists. `LastIndex1` returns `-1` when no bits are
set. `OnesCountRange` counts set positions in `[l, r)` and returns zero when
`l >= r`. `TrailingZeros` is equivalent to `Index1`; `Len` is one plus the
highest set position, or zero when empty. `AllIndex1` returns set positions in
strict ascending order. `String` returns the base-2 digits from the highest
set bit to bit zero, with no leading zeroes; it returns `""` when empty.

Implement range, shift, arithmetic, and relation operations:

```go
func (b Bitset) SetRange(l, r int)
func (b Bitset) ResetRange(l, r int)
func (b Bitset) FlipRange(l, r int)
func (b Bitset) ResetFrom(start int)
func (b Bitset) Lsh(k int)
func (b Bitset) Rsh(k int)
func (b Bitset) Add(i int)
func (b Bitset) Sub(i int)
func (b Bitset) Or(c Bitset)
func (b Bitset) And(c Bitset)
func (b Bitset) Xor(c Bitset)
func (b Bitset) Equals(c Bitset) bool
func (b Bitset) HasSubset(c Bitset) bool
```

The range methods mutate `[l, r)` and do nothing when `l >= r`. `ResetFrom`
clears every bit at or above `start`. `Lsh` and `Rsh` shift all storage bits by
`k`, filling vacated positions with zero; a shift at least the storage capacity
clears the bitset. The storage has no separate logical-length mask, so a left
shift may leave set bits anywhere in its allocated words. `Add(i)` adds
`1 << i` using binary carry through the stored words. `Sub(i)` subtracts
`1 << i` using binary borrow. `Or`, `And`, and `Xor` mutate `b` word-by-word;
the two operands have equal length. `Equals` compares equal-length bitsets.
`HasSubset(c)` is true exactly when every bit set in `c` is also set in `b`.

For example, after `b := NewBitset(64)`, `b.Set(1)`, `b.SetRange(4, 7)`, and
`b.Flip(5)`, `b.AllIndex1()` is `[]int{1, 4, 6}` and `b.String()` is
`"1010010"`. Calling `b.Lsh(1)` then produces positions `2`, `5`, and `7`.

## Implementation Notes

The module uses the standard-library-only offline build contract and the bridge
must remain outside the candidate package. The bridge sends one JSON request
per line and expects exactly one JSON response per request. It has operation
names `summary`, `ranges`, `search`, `shift`, `arithmetic`, `relation`, and
`has`; each operation starts from positions supplied by the request and returns
JSON values derived from the public methods above. The bridge rejects malformed
JSON, more than 16 storage words, indexes outside the allocated capacity,
malformed ranges, and unknown operations before invoking the package. It must
not emit diagnostics to stdout or panic on bad bridge input.

Preserve deterministic results and do not mutate the argument bitset in
`Equals` or `HasSubset`. The evaluator checks ordinary single-word and
cross-word cases, empty values, inclusive searches at word boundaries, carries
and borrows, equal-length relations, and bounded invalid bridge requests.

## Examples

```go
import "github.com/EndlessCheng/codeforces-go/copypasta"

b := copypasta.NewBitset(128)
b.Set(3)
b.SetRange(8, 11)
positions := b.AllIndex1()
```

```go
b := copypasta.NewBitset(64)
b.Set(63)
b.Lsh(1)
// The shift fills vacated positions with zero.
```

```go
b := copypasta.NewBitset(16)
b.SetRange(2, 6)
count := b.OnesCountRange(2, 6) // 4
```

## Error Handling and Boundary Conditions

The public methods receive indexes and ranges bounded by the bitset capacity.
Range operations are half-open and are no-ops when the start is not less than
the end. Searches use the capacity sentinel when no bit matches; `LastIndex1`
uses `-1` for an empty bitset. Shifts at or beyond capacity clear storage.
Relation methods do not mutate either operand. Malformed bridge input, unknown
operation names, or out-of-range positions are rejected by the bridge before
package calls and must produce no diagnostic on stdout.
