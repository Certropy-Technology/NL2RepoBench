# Build `go-concurrent-map`

## Project Description

Create a Go module with module path `github.com/orcaman/concurrent-map/v2` and
root package name `cmap`. It provides a sharded, concurrency-safe generic map
with string-key and comparable-key constructors. The implementation must be
usable on Linux/amd64 with Go 1.26.5 and no network access.

## Supports

- A single root `go.mod` and `go.sum`; use `GOWORK=off`, `GOPROXY=off`,
  `GOSUMDB=off`, `GOTOOLCHAIN=local`, and `CGO_ENABLED=0`.
- Standard-library dependencies only. Do not use cgo, unsafe, plugins,
  external services, network access, or external replace directives.
- Generic values of any type and comparable keys where the documented
  constructor permits them.
- Safe concurrent reads and writes to distinct keys.

## Natural Language Instruction

Create the generic `github.com/orcaman/concurrent-map/v2` module from an empty
workspace. Implement constructors, sharded map mutation, lookup, iteration,
counting, and deterministic serialization behavior in the API guide.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
├── concurrent_map.go
├── concurrent_map_shard.go
└── concurrent_map_shared.go
```

Keep the root package name `cmap` and all generic signatures. No verifier files
or runtime network access are part of this project.

## Examples

```go
m := New[int](); m.Set("count", 1); value, ok := m.Get("count")
```

```go
added := m.SetIfAbsent("count", 2); keys := m.Keys()
```

## Error Handling and Boundary Conditions

Preserve absent-key zero values, duplicate insertion, empty maps, comparable
key restrictions, concurrent distinct-key operations, stable returned slices,
and JSON/iteration order contracts. Do not introduce global mutable state.

```go
import cmap "github.com/orcaman/concurrent-map/v2"
```

## API Usage Guide

Implement these public declarations in package `cmap`:

```go
type ConcurrentMap[K comparable, V any] struct{}
func New[V any]() ConcurrentMap[string, V]
func NewStringer[K interface{ fmt.Stringer; comparable }, V any]() ConcurrentMap[K, V]
func NewWithCustomShardingFunction[K comparable, V any](func(K) uint32) ConcurrentMap[K, V]
func (m ConcurrentMap[K, V]) Set(K, V)
func (m ConcurrentMap[K, V]) MSet(map[K]V)
func (m ConcurrentMap[K, V]) SetIfAbsent(K, V) bool
func (m ConcurrentMap[K, V]) Get(K) (V, bool)
func (m ConcurrentMap[K, V]) Has(K) bool
func (m ConcurrentMap[K, V]) Remove(K)
func (m ConcurrentMap[K, V]) Pop(K) (V, bool)
func (m ConcurrentMap[K, V]) Count() int
func (m ConcurrentMap[K, V]) IsEmpty() bool
func (m ConcurrentMap[K, V]) Clear()
func (m ConcurrentMap[K, V]) Items() map[K]V
func (m ConcurrentMap[K, V]) Keys() []K
func (m ConcurrentMap[K, V]) IterBuffered() <-chan Tuple[K, V]
func (m ConcurrentMap[K, V]) IterCb(func(K, V))
func (m ConcurrentMap[K, V]) Upsert(K, V, UpsertCb[V]) V
func (m ConcurrentMap[K, V]) RemoveCb(K, RemoveCb[K, V]) bool
func (m ConcurrentMap[K, V]) MarshalJSON() ([]byte, error)
func (m *ConcurrentMap[K, V]) UnmarshalJSON([]byte) error
```

`New` creates a usable empty string-key map. `Set` replaces a value, `Get`
returns the zero value and `false` for an absent key, and `SetIfAbsent` returns
`true` only when it inserts. `Remove` is idempotent; `Pop` returns and removes
the current value. `Count`, `IsEmpty`, `Items`, and `Keys` describe the map at
the time of their operation. `MSet` inserts or replaces every supplied entry.

`Upsert` invokes its callback while the target shard is locked. The callback
receives whether the key existed, its previous value (or zero value), and the
new value, and its return value becomes the stored value. `RemoveCb` invokes
its callback with key, current value, and existence; it removes the entry only
when the callback returns `true` and the key exists. Callback code must not
re-enter the same shard.

`IterBuffered` yields each key/value pair present in a bounded snapshot and
then closes its channel. `IterCb` invokes a callback once per current entry.
Iteration order and key order are unspecified. `Clear` removes all entries.
JSON marshaling uses the underlying map's JSON object representation for keys
that JSON supports; unmarshaling adds decoded entries to the map.

## Implementation Notes

Methods returning keys or values provide the documented snapshot semantics, so
callers can inspect results after a map change. Hashing and shard selection are
implementation details; lookup and mutation results remain deterministic.

Use sharding and locks to prevent concurrent map read/write races. Preserve
zero values for missing keys, avoid exposing internal mutable maps through
updates, and ensure callbacks receive the documented existence flag. The
typed subprocess bridge used by evaluation exercises deterministic string
values and bounded operation sequences; it does not require a particular
shard count or iteration order.
