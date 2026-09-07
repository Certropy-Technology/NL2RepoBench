# Build `go-set`

## Project Description

Create the core set profile of the pure-Go module
`github.com/deckarep/golang-set/v2` at the repository root. Its root package is
named `mapset` and provides generic set collections for comparable Go values.
The evaluated behavior is deterministic Linux/amd64 behavior and must not
require a service, cgo, generated code, or mutable global state outside the set
instances. Only the API listed below belongs to this task's evaluated profile.

## Supports

- Go `1.26.5`, Linux/amd64, `CGO_ENABLED=0`, and exactly one root `go.mod`.
- Module path `github.com/deckarep/golang-set/v2` and package name `mapset`.
- Offline compilation with `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
  `GOTOOLCHAIN=local`, and `-mod=vendor`.
- The root `go.mod` must require `go.mongodb.org/mongo-driver v1.17.9`. Harbor
  supplies that exact module in the offline vendor tree because the frozen
  module contract includes serialization method types. The evaluated methods
  below otherwise need only the standard library. Do not add another
  dependency, runtime service, CLI, cgo, plugin, unsafe code, or replace rule.
- The set element type must be comparable, and operations must preserve set
  uniqueness.

## Natural Language Instruction

Create the generic `github.com/deckarep/golang-set/v2` module from an empty
workspace. Implement the comparable-element set constructors, set operations,
iterators, conversion helpers, and deterministic ordering behavior listed below.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
├── mapset.go
├── thread_safe.go
└── iterator.go
```

Expose the root package as `mapset` and preserve the generic signatures. The
MongoDB serialization types required by the public method signatures must use
the declared offline dependency; no service or evaluation-only files belong in
the project.

## Examples

```go
s := mapset.NewSet(1, 2); s.Add(3); present := s.Contains(2)
```

```go
it := s.Iterator(); for value := range it.C { _ = value }
```

## Error Handling and Boundary Conditions

Preserve uniqueness, empty sets, duplicate additions, absent removals, nil
iterators, comparable-type restrictions, copy behavior, and deterministic
`Sorted` output. Concurrent-safe and thread-unsafe constructors must retain
their documented distinction.

```go
import mapset "github.com/deckarep/golang-set/v2"
```

## API Usage Guide

Import `github.com/deckarep/golang-set/v2` with the package name `mapset`.

```go
type Set[T comparable] interface {
    Add(value T) bool
    Append(values ...T) int
    AppendFrom(other Set[T]) int
    Cardinality() int
    Clear()
    Clone() Set[T]
    Contains(values ...T) bool
    ContainsOne(value T) bool
    ContainsAny(values ...T) bool
    ContainsAnyElement(other Set[T]) bool
    Difference(other Set[T]) Set[T]
    Intersect(other Set[T]) Set[T]
    IsEmpty() bool
    IsProperSubset(other Set[T]) bool
    IsProperSuperset(other Set[T]) bool
    IsSubset(other Set[T]) bool
    IsSuperset(other Set[T]) bool
    Equal(other Set[T]) bool
    Union(other Set[T]) Set[T]
    Remove(value T)
    RemoveAll(values ...T)
    ToSlice() []T
    Each(fn func(T) bool)
    Filter(fn func(T) bool) Set[T]
    SymmetricDifference(other Set[T]) Set[T]
    Pop() (T, bool)
    PopN(n int) ([]T, int)
}

func NewSet[T comparable](values ...T) Set[T]
func NewSetWithSize[T comparable](cardinality int) Set[T]
func NewSetFromMapKeys[T comparable, V any](values map[T]V) Set[T]
func NewThreadUnsafeSet[T comparable](values ...T) Set[T]
func NewThreadUnsafeSetWithSize[T comparable](cardinality int) Set[T]
```

`NewSet` returns a set suitable for concurrent reads and writes. The verifier
may have several goroutines call `Add` on that set at the same time.
`NewSetWithSize` returns an empty set with a non-negative capacity hint. The
thread-unsafe constructors have the same value semantics but do not add
concurrency protection. Constructors deduplicate repeated values.

`Add` reports whether the value was newly inserted. `Append` inserts all values
and reports the number of newly inserted values. `AppendFrom` does the same for
the members of another set created by the same constructor family. `Remove`
deletes one value. `RemoveAll` deletes all listed values and ignores absent
values. `Contains` is true only when every listed value is present; with no
arguments it is true. `ContainsOne` checks one value. `ContainsAny` is true
when at least one listed value is present and false when called without values.
`ContainsAnyElement` checks whether two compatible sets overlap.
`Cardinality` counts unique elements, `IsEmpty` reports whether that count is
zero, `Clear` removes all elements, and `ToSlice` returns the members in an
unspecified order. The returned slice is caller-owned.

`Union`, `Intersect`, `Difference`, and `SymmetricDifference` return new sets
and do not mutate their inputs. `IsSubset` and `IsSuperset` allow equality.
Their proper variants require unequal cardinalities. `Equal` compares
membership without regard to insertion order. These binary operations receive
sets created by the same constructor family in this profile.

`Clone` returns an independent set. `Each` invokes its callback once per member
until the callback returns true. `Filter` returns a new set containing members
whose callback result is true, without changing the receiver. Callback and
slice order are unspecified.

`Pop` removes and returns an arbitrary member with `ok=true`. On an empty set it
returns the zero value of `T` with `ok=false`. `PopN` removes and returns up to
`n` arbitrary members plus the number actually removed. A non-positive `n` or
an empty set returns a non-nil empty slice and zero. If `n` is larger than the
cardinality, `PopN` removes every member.

Example:

```go
left := mapset.NewSet("red", "green", "red")
right := mapset.NewSet("green", "blue")
combined := left.Union(right)
// left.Cardinality() == 2
// combined.Cardinality() == 3
```

## Implementation Notes

Keep all state instance-local and use a map-backed representation or another
bounded deterministic structure. Methods that return sets must not alias the
mutable storage of their inputs. The evaluator calls the public API through a
separate typed newline-delimited JSON bridge; it never imports candidate code
into the evaluator. Do not hard-code private requests or write evaluator
reports, rewards, or test results from candidate code. Random iteration order
is acceptable where the API documents arbitrary order, so callers should sort
only when they need presentation order.

Iterator channels, iterator objects, string formatting, JSON/BSON codecs, and
convenience functions outside the signatures above are not part of this task.
