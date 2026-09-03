# Build `golang.org/x/sync/errgroup`

## Project Description

Create a self-contained Go module whose module path is exactly
`golang.org/x/sync` and whose primary package is
`golang.org/x/sync/errgroup`. The package coordinates goroutines that perform
parts of one task, returns the first non-nil error, and optionally cancels a
derived context. Implement the `errgroup` package only; other packages that
may exist in the upstream repository are outside this task.

## Supports

- Linux/amd64 with Go `1.26.5`, `CGO_ENABLED=0`, and exactly one root
  `go.mod` plus `go.sum`.
- Standard-library dependencies only. Builds and tests must work with
  `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`, `GOTOOLCHAIN=local`, and a
  pre-existing vendor directory. Do not use cgo, unsafe code, plugins,
  external services, or network access.
- The package must be safe for concurrent goroutines according to the API
  rules below. Do not add command-line programs or perform I/O from package
  methods.

## API Usage Guide

Import the package as `golang.org/x/sync/errgroup`.

### `Group`

```go
type Group struct{}

func (g *Group) Go(f func() error)
func (g *Group) TryGo(f func() error) bool
func (g *Group) SetLimit(n int)
func (g *Group) Wait() error
```

A zero `Group` is ready to use, has no active-goroutine limit, and does not
cancel anything. `Go` starts `f` in a new goroutine. When a function returns a
non-nil error, the group keeps the first such error it observes, and `Wait`
blocks until all functions started by `Go` or `TryGo` finish before returning
that error. When all functions return nil, `Wait` returns nil. A function panic
is not converted into an error.

`Wait` may be called after all starts have been issued and may be called again;
it returns the same result. A group should not be reused for a different task.
The first call that adds work must happen before `Wait`.

`SetLimit(n)` changes the maximum number of active functions. A negative `n`
means unlimited; zero prevents new functions from starting; a positive `n`
allows at most `n` active functions. Do not change the limit while any
function in the group is active. With a limit, `Go` blocks until it can add a
function without exceeding the limit. `TryGo` never blocks: it starts `f` and
returns true when a slot is immediately available, otherwise it returns false
and does not call `f`. After active functions finish, a previously rejected
`TryGo` may succeed.

`SetLimit` is a configuration operation. Setting a non-negative limit creates a
new capacity bound; setting a negative limit removes the bound. A limit change
while work is active must report the documented misuse, normally by panicking.

### `WithContext`

```go
func WithContext(ctx context.Context) (*Group, context.Context)
```

`WithContext` returns a new group and a derived context. The derived context
inherits cancellation from `ctx`. It is canceled the first time a function
passed to `Go` or `TryGo` returns a non-nil error, or when `Wait` returns if no
function has produced an error. The first error is the cancellation cause;
when there is no function error, the cause is `context.Canceled`. `Wait`
returns the same first error or nil as for a zero group. Work functions may
observe `ctx.Done()` and should stop their own work after cancellation.

## Implementation Notes

Use synchronization primitives from the standard library to protect the first
error and to wait for every started function. Preserve the first-error
semantics under concurrent completion, and release any configured capacity
when a function exits, including when it returns an error. `TryGo` must not
start a function when it reports false. Keep context cancellation and error
selection independent of completion ordering except for the documented first
observed error.

The evaluator uses a bounded newline-delimited JSON subprocess bridge. Its JSON
operation names and cases are private; implement the public package APIs rather
than matching a bridge fixture. The bridge checks nil and non-nil completion,
context cancellation causes, bounded concurrency, blocking `Go`, `TryGo`
recovery, unlimited and zero limits, and malformed-operation errors.
