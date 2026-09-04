# Recreate the go.uber.org/dig dependency injection container

## Project Description

Create a Go module at the repository root with module path `go.uber.org/dig`.
Reproduce the deterministic, in-process dependency injection behavior exercised by
the typed bridge. The package uses reflection to inspect constructors, build a
dependency graph, cache constructed values, and invoke functions after resolving
their dependencies.

## Supports

- Linux/amd64, Go `1.26.5`, `CGO_ENABLED=0`, `GOWORK=off`.
- Offline builds with `GOPROXY=off`, `GOSUMDB=off`, `GOTOOLCHAIN=local`, and
  `go test -mod=vendor ./...`.
- A root `go.mod` declaring exactly `go 1.26.5`, a valid `go.sum`, and an
  offline vendor directory. The runtime package must not require third-party
  modules, cgo, plugins, unsafe code, files, network access, or global mutable
  state.
- The evaluator sends newline-delimited JSON requests to a child-side bridge.
  Candidate code must not write diagnostics to stdout or create verifier-owned
  reports.

## API Usage Guide

Implement the public package `go.uber.org/dig` with these core APIs and types:

```go
func New(opts ...Option) *Container
func (c *Container) Provide(constructor interface{}, opts ...ProvideOption) error
func (c *Container) Invoke(function interface{}, opts ...InvokeOption) error
func (c *Container) Decorate(decorator interface{}, opts ...DecorateOption) error
func (c *Container) Scope(name string, opts ...ScopeOption) *Scope
func (c *Container) String() string
func (c *Scope) Provide(constructor interface{}, opts ...ProvideOption) error
func (s *Scope) Invoke(function interface{}, opts ...InvokeOption) error
func (s *Scope) Decorate(decorator interface{}, opts ...DecorateOption) error
func (s *Scope) Scope(name string, opts ...ScopeOption) *Scope
func Visualize(c interface{}, w io.Writer, opts ...VisualizeOption) error
func CanVisualizeError(err error) bool
func IsCycleDetected(err error) bool
func RootCause(err error) error
```

Support the constructor and result conventions used by the bridge:

- A constructor is a function whose arguments are dependencies and whose return
  values are values to cache; its final return value may be an `error`, which
  aborts construction when non-nil.
- `dig.In` embedded in a parameter struct requests fields by type. Field tags
  `name:"x"`, `group:"g"`, and `optional:"true"` select named, grouped, and
  optional dependencies. `dig.Out` embedded in a result struct publishes tagged
  named/grouped fields.
- `Name`, `Group`, `As`, `Export`, `FillProvideInfo`, and `LocationForPC` are
  `ProvideOption` constructors. `FillInvokeInfo` is an `InvokeOption` and
  `FillDecorateInfo` is a `DecorateOption`; their info structures expose the
  inspected input/output type strings and constructor IDs.
- `DryRun`, `RecoverFromPanics`, and `DeferAcyclicVerification` are container
  options. `RecoverFromPanics` converts constructor/invoke panics to
  `PanicError`; without it, panics propagate.
- Constructors are called once per container/scope and cached. A second Invoke
  reuses the cached value. A missing dependency, invalid constructor, duplicate
  provider, or cycle returns a non-nil error. `IsCycleDetected` identifies cycle
  errors and `RootCause` unwraps the underlying cause.
- `Scope` inherits providers from its parent while allowing child-only values;
  child values are not visible in the parent. `Decorate` replaces or transforms
  an existing value in the current scope.

## Implementation Notes

Use reflection only inside the candidate process and preserve exact Go type
identity, field-tag semantics, deterministic caching, and error propagation.
The bridge uses fixed typed constructors and serializable summaries; arbitrary
reflection values, caller-owned callback state, visualization writers, and
private internal packages are outside this task's JSON contract. Do not copy the
upstream implementation or tests into the public workspace.
