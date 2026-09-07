# Build a generic Go data-structure library

## Project Description

Create the Go module `github.com/emirpasic/gods/v2` at repository root. It is a
pure-Go collection of reusable generic containers. The evaluation exercises the
observable behavior of representative lists, stacks, queues, maps, sets, and a
binary heap through a JSON subprocess bridge. Implement the library from an
empty workspace; do not assume any source files are provided.

## Supports

- Linux/amd64 with Go `1.26.5` and one root `go.mod` whose module path is
  `github.com/emirpasic/gods/v2`.
- Use Go generics where the API requires them. The module must build with
  `GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off GOPROXY=off
  GOSUMDB=off GOTOOLCHAIN=local` and `go test -mod=vendor ./...` without a
  network connection.
- Do not use cgo, plugins, external services, workspace files, or external
  `replace` directives. Keep the public package import paths described below.

## Natural Language Instruction

Create the generic `github.com/emirpasic/gods/v2` module from an empty
workspace. Implement the listed lists, stacks, queues, maps, sets, and heap
containers with their constructors, mutation, lookup, iteration, and ordering
contracts.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
├── lists/
├── stacks/
├── queues/
├── maps/
├── sets/
└── trees/
```

Preserve every import path explicitly listed in the API guide and use Go
generics where required. Do not include private verifier files.

## Examples

```go
list := arraylist.New[int](); list.Add(1); value, ok := list.Get(0)
```

```go
queue := linkedlistqueue.New[int](); queue.Enqueue(2); item, ok := queue.Dequeue()
```

## Error Handling and Boundary Conditions

Honor empty-container behavior, absent keys/indexes, duplicate set values,
heap ordering, iterator exhaustion, nil values, and deterministic traversal
contracts. Container methods must remain local and offline.

## API Usage Guide

All imports use the module prefix `github.com/emirpasic/gods/v2`.

### Shared container behavior

The concrete containers below are not safe for concurrent mutation. `New`
constructors return empty containers unless values are explicitly listed. A
zero-value lookup returns the Go zero value together with `false` when the
element is absent. `Empty`, `Size`, `Clear`, `Values`, and `String` have the
obvious container-wide meaning; `Values` returns a copy in the container's
documented order.

### Lists

`lists/arraylist.List[T comparable]` provides:

```go
func New[T comparable](values ...T) *List[T]
func (list *List[T]) Add(values ...T)
func (list *List[T]) Get(index int) (T, bool)
func (list *List[T]) Remove(index int)
func (list *List[T]) Contains(values ...T) bool
func (list *List[T]) Values() []T
func (list *List[T]) IndexOf(value T) int
func (list *List[T]) Empty() bool
func (list *List[T]) Size() int
func (list *List[T]) Clear()
func (list *List[T]) Sort(comparator utils.Comparator[T])
func (list *List[T]) Swap(i, j int)
func (list *List[T]) Insert(index int, values ...T)
func (list *List[T]) Set(index int, value T)
```

`Get` and `Remove` ignore invalid indexes. `Insert` and `Set` accept an index
equal to the current size as append, but ignore negative or larger indexes.
`Sort` mutates the list using a comparator returning negative, zero, or
positive. `lists/singlylinkedlist` and `lists/doublylinkedlist` expose the
same core methods plus `Append` and `Prepend`; their `Values` order is the
logical list order.

### Stacks and queues

`stacks/arraystack.Stack[T comparable]` and
`stacks/linkedliststack.Stack[T comparable]` provide:

```go
func New[T comparable]() *Stack[T]
func (stack *Stack[T]) Push(value T)
func (stack *Stack[T]) Pop() (T, bool)
func (stack *Stack[T]) Peek() (T, bool)
func (stack *Stack[T]) Empty() bool
func (stack *Stack[T]) Size() int
func (stack *Stack[T]) Clear()
func (stack *Stack[T]) Values() []T
```

`Pop` is LIFO and `Values` is also LIFO, with the next value to pop first.
`queues/arrayqueue.Queue[T comparable]` and
`queues/linkedlistqueue.Queue[T comparable]` provide the analogous
`New`, `Enqueue`, `Dequeue`, `Peek`, `Empty`, `Size`, `Clear`, and `Values`
methods; they are FIFO. `queues/circularbuffer.New[T comparable](maxSize)`
requires a positive capacity, drops the oldest item when full, and provides
`Full` in addition to the queue methods.

### Maps and sets

`maps/hashmap.Map[K comparable, V any]` and
`maps/linkedhashmap.Map[K comparable, V any]` provide `New`, `Put`, `Get`,
`Remove`, `Empty`, `Size`, `Clear`, `Keys`, `Values`, and `String`.
Hash-map order is unspecified; linked-hash-map order follows insertion order.

`maps/treemap.Map[K cmp.Ordered, V any]` provides the same map methods with
sorted key order, plus:

```go
func (m *Map[K, V]) Min() (K, V, bool)
func (m *Map[K, V]) Max() (K, V, bool)
func (m *Map[K, V]) Floor(key K) (K, V, bool)
func (m *Map[K, V]) Ceiling(key K) (K, V, bool)
```

`sets/hashset.Set[T comparable]` provides `New`, `Add`, `Remove`, `Contains`,
`Empty`, `Size`, `Clear`, `Values`, `String`, `Intersection`, `Union`, and
`Difference`. `sets/treeset.Set[T cmp.Ordered]` provides the same set
operations and returns sorted values. Set membership is unique even when an
item is added repeatedly.

### Heap and comparator

`trees/binaryheap.New[T cmp.Ordered]()` returns a min-heap and
`NewWith(comparator)` supports a custom ordering. The heap provides `Push`
(including multiple values), `Pop`, `Peek`, `Empty`, `Size`, `Clear`, and
`Values`; `Pop` and `Peek` return the current root. The comparator type is
`utils.Comparator[T] func(x, y T) int`.

### Serialization

Concrete containers with serialization support provide `ToJSON() ([]byte,
error)`, `FromJSON([]byte) error`, and compatible `MarshalJSON`/
`UnmarshalJSON` methods. JSON round trips preserve the logical values and
ordering where the container defines an order. Invalid JSON returns an error.

## Implementation Notes

Keep package boundaries and exported names compatible with the API guide.
Pointer receivers must preserve container mutation. Empty results should be
usable by callers and should not expose internal slices or maps for mutation.
The bridge sends bounded JSON requests to a candidate subprocess; therefore
public methods used by the bridge must be deterministic, panic-free for the
documented inputs, and must not print diagnostics to stdout. Do not add a
`main` package or hard-code evaluator data into the library.
