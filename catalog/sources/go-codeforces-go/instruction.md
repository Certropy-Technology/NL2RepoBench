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

## Supports

- Go `1.26.5`, Linux/amd64, `CGO_ENABLED=0`.
- A root `go.mod` declaring exactly `module github.com/EndlessCheng/codeforces-go`
  and `go 1.26.5`, plus a `go.sum` and an offline `vendor/` directory.
- Offline builds with `GOWORK=off GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local`
  and `go build -mod=vendor`.
- Standard library imports only. Do not add a workspace, `replace` directive,
  plugins, cgo, external commands, or background work.

## API Usage Guide

Put the implementation in package `copypasta` at `copypasta/`. Define:

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

The bridge sends one JSON request per line and expects exactly one JSON response
per request. It has operation names `summary`, `ranges`, `search`, `shift`,
`arithmetic`, `relation`, and `has`. Each operation starts from positions supplied by
the request and returns JSON values derived from the public methods above. The
bridge rejects malformed JSON, more than 16 storage words, indexes outside the
allocated capacity, malformed ranges, and unknown operations before invoking
the package. It must not emit diagnostics to stdout or panic on bad bridge
input.

Preserve deterministic results and do not mutate the argument bitset in
`Equals` or `HasSubset`. The evaluator checks ordinary single-word and
cross-word cases, empty values, inclusive searches at word boundaries, carries
and borrows, equal-length relations, and bounded invalid bridge requests.
