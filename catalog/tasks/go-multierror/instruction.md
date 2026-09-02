# `go-multierror`

## Project Description

Create a self-contained Go module that aggregates several ordinary `error`
values into one error while preserving useful inspection and formatting
behavior. The module path must be exactly
`github.com/hashicorp/go-multierror`, and the package at the module root must
be named `multierror`.

## Supports

- Linux/amd64 with Go `1.26.5`.
- One root `go.mod` and `go.sum`; build with `GOWORK=off`, `GOPROXY=off`,
  `GOSUMDB=off`, `GOTOOLCHAIN=local`, and `CGO_ENABLED=0`.
- Standard-library dependencies only. Do not use cgo, plugins, unsafe code,
  workspaces, external replacements, network access, or external services.
- The public API must be usable by callers that provide ordinary values from
  the standard `errors` and `sort` packages.

## API Usage Guide

Implement package `multierror` with these public declarations and behaviors.

### `Error` and formatting

```go
type Error struct {
    Errors []error
    ErrorFormat ErrorFormatFunc
}

type ErrorFormatFunc func([]error) string

func (e *Error) Error() string
func (e *Error) ErrorOrNil() error
func (e *Error) GoString() string
func (e *Error) WrappedErrors() []error
func (e *Error) Unwrap() error
func (e *Error) Len() int
func (e Error) Swap(i, j int)
func (e Error) Less(i, j int) bool

func ListFormatFunc(es []error) string
```

`Error` implements the standard `error` interface. When `ErrorFormat` is nil,
`Error()` uses `ListFormatFunc`. For one error the default text is exactly:

```text
1 error occurred:
\t* <error text>

```

For multiple errors it is exactly `<n> errors occurred:` followed by each
error as a tab-indented `* <error text>` line, then two final newlines. The
order is the order in `Errors`. A non-nil `ErrorFormat` is called with the
current slice and its returned string is used unchanged.

`ErrorOrNil` returns nil for a nil receiver or an `Error` with no entries;
otherwise it returns the receiver as an `error`. `WrappedErrors` returns nil
for a nil receiver and otherwise the current `Errors` slice. `Len` is safe on
a nil receiver and returns zero there. `Less` compares `Errors[i].Error()`
lexicographically, and `Swap` exchanges two entries so `*Error` can be passed
to `sort.Sort`.

`Unwrap` returns nil for a nil or empty receiver, the sole contained error for
one entry, and a deterministic chain for multiple entries. Repeated
`errors.Unwrap` calls must expose the contained errors in their original
order, after which they return nil. The chain must also allow standard
`errors.Is` and `errors.As` to find matching nested errors.

### Construction and transformations

```go
func Append(err error, errs ...error) *Error
func Flatten(err error) error
func Prefix(err error, prefix string) error
```

`Append` returns a mutable `*Error`. A nil first argument starts an empty
aggregation. A non-multierror first argument becomes the first entry. Nil
arguments are ignored. A non-nil `*Error` argument in `errs` contributes its
entries rather than becoming one nested entry. A typed-nil `*Error` is ignored
and must not panic. Existing entries remain before appended entries.

`Flatten` returns non-`*Error` inputs unchanged. For an `*Error`, recursively
replace nested `*Error` entries with their leaf errors in depth-first order
and return one `*Error`. The resulting empty error is still a non-nil
`*Error` value.

`Prefix` returns nil for a nil input. For a regular error it returns an error
whose text is `<prefix> <original text>`. For an `*Error`, prefix every
contained error in place and preserve the multierror type and order. A single
space separates prefix and message, including when either string is empty.

### Concurrent collection

```go
type Group struct{}

func (g *Group) Go(f func() error)
func (g *Group) Wait() *Error
```

`Group.Go` runs the function asynchronously. Every non-nil returned error is
collected, and `Wait` blocks until all started functions finish and returns
the collected `*Error`, or nil if all functions returned nil. The API must be
safe when multiple functions report errors. Completion order is not part of
the contract; callers must not rely on an order among concurrently returned
errors.

## Implementation Notes

Keep behavior deterministic wherever the public contract specifies an order,
and avoid exposing internal implementation details. Preserve standard error
wrapping behavior for `errors.Is`, `errors.As`, and `errors.Unwrap`. Do not
perform I/O, start processes, or access the network from library methods.
The evaluation uses a bounded JSON subprocess bridge that exercises the API
without importing candidate code into the trusted verifier. It includes empty,
Unicode, nested, nil, custom-format, wrapping, sorting, and concurrent-group
cases.
