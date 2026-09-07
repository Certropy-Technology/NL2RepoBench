## Project Description

Build a Go module whose module path is `go.uber.org/dig`. It is an in-process,
reflection-based dependency-injection container for Go programs. The intended
users are Go applications that register constructors, resolve their typed
dependencies, and invoke application functions without wiring every argument
manually.

The candidate must provide the public package at the module root. It must be
able to inspect function signatures, construct a dependency graph, cache values
per container, inject named and grouped values, populate `dig.In` and
`dig.Out` structs, create child scopes, decorate existing values, and report
invalid graphs and construction failures as errors. A constructor may return an
ordinary value or values followed by an `error`; a non-nil final error prevents
the requested operation from completing.

The observable boundary is the package API used by a fixed typed bridge. The
bridge exercises fixed, JSON-summary-friendly constructors and functions, so
the implementation must preserve Go type identity and reflection behavior for
those calls. The task does not require a command-line application, a network
service, file or database persistence, plugins, cgo, unsafe code, or global
mutable state. Arbitrary caller-owned callbacks, arbitrary non-JSON reflection
values, and graph visualization through caller-owned writers are package APIs
but are not part of the typed bridge contract.

## Supports

- Runtime: Linux/amd64, Go `1.26.5`, `CGO_ENABLED=0`, `GOWORK=off`.
- The repository root is an installable Go module with module path
  `go.uber.org/dig`, a `go 1.26.5` directive, valid module metadata, and an
  offline vendor directory when dependencies are declared.
- Build and test with no network access:

  ```text
  GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local \
  GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off \
  go test -mod=vendor ./...
  ```

- The runtime package should have no third-party runtime dependency. If build
  or test metadata requires a dependency, it must be available in `vendor/`
  and must not require downloading from a module proxy. Do not contact GitHub,
  a Go proxy, DNS, or any external service at build or runtime.
- The evaluation harness creates and runs its child-side typed bridge. The
  candidate supplies the package implementation, not a verifier, private
  tests, a reward writer, or bridge-owned reports. Candidate diagnostics must
  not be written to the bridge's stdout.
- There is no standalone CLI for this library. The exact supported entry point
  is Go package import:

  ```go
  import "go.uber.org/dig"
  c := dig.New()
  ```

  The required project layout is:

  ```text
  workspace/
  ├── go.mod
  ├── go.sum
  ├── vendor/
  │   └── modules.txt
  ├── container.go
  ├── constructor.go
  ├── scope.go
  ├── options.go
  ├── error.go
  ├── visualize.go
  └── *_test.go
  ```

  File names may be organized differently, but the root package must expose
  the import path and APIs below. Tests are optional project files and must not
  replace the package implementation.

## API Usage Guide

### `dig.New`

Import path: `go.uber.org/dig`.

```go
func New(opts ...Option) *Container
```

Create an empty container. Options configure container-wide policy at creation
time. The returned pointer owns its provider graph and cache; creating another
container does not share registrations or constructed values. With no options,
normal cycle checking and panic propagation apply.

```go
c := dig.New()
```

An ordinary call returns a usable empty `*dig.Container`. The edge case
`dig.New(dig.DryRun(true), dig.RecoverFromPanics())` must still return a usable
container, with those policies applying to subsequent operations. `New` does
not perform constructor calls merely because a provider will later be added.

### `Container.Provide`

```go
func (c *Container) Provide(constructor interface{}, opts ...ProvideOption) error
```

Register a constructor in `c`. The input must be a function. Its parameters are
dependencies requested by type; its return values are values made available to
later operations. A final return value of type `error` is treated as the
constructor error channel rather than as a provided dependency. `Name`, `Group`,
`As`, and the other provide options below modify the registration.

`Provide` updates the graph and returns `nil` when the registration is valid.
It returns a non-nil error for a non-function or otherwise invalid constructor,
an invalid option combination, or a duplicate provider that cannot coexist in
the same key. Registration itself normally does not call the constructor;
construction is demand-driven by `Invoke` or another resolution. The method
must not mutate a parent scope when called on a child scope.

```go
err := c.Provide(func() string { return "configured" })
err = c.Provide(func(s string) int { return len(s) })
```

The empty-input edge case is a zero-argument, one-result constructor such as
`func() string { return "" }`; it is valid and provides an empty string. A
constructor value such as `42` is invalid and must return an error without
being registered.

### `Container.Invoke`

```go
func (c *Container) Invoke(function interface{}, opts ...InvokeOption) error
```

Resolve the parameters of `function` from `c` and call it. The input must be a
function; its arguments are dependencies and its return values are not
registered as providers. A zero-argument function is valid. `Invoke` returns
`nil` after the function returns successfully, and a non-nil error when a
dependency is missing, resolution or construction fails, the function is
invalid, or an invocation option rejects the request.

Constructors are demand-driven and cached: a successful constructor is called
at most once per container (or scope) for its dependency key, and subsequent
invocations reuse its value. A constructor returning a non-nil final error is
not considered successfully cached. Without `RecoverFromPanics`, a panic from
a constructor or invoked function propagates. With it, the panic is returned
as a `PanicError`.

```go
var got int
err := c.Invoke(func(n int) { got = n })
```

For the edge case `c.Invoke(func() {})`, the function is called once without
requiring any provider. Invoking a function that requests an unregistered type,
such as `func(bool) {}`, returns an error and does not call the function.

### `Container.Decorate`

```go
func (c *Container) Decorate(decorator interface{}, opts ...DecorateOption) error
```

Register a decorator function for an existing value in the current container.
The decorator is a function whose input identifies the value to transform and
whose output supplies its replacement, following the same typed reflection
rules as other container functions. Decoration affects resolution in this
container and does not write to a parent or sibling scope. Invalid decorator
values, missing targets, duplicate/conflicting decoration, or invalid options
return an error.

```go
c.Provide(func() string { return "raw" })
err := c.Decorate(func(s string) string { return "[" + s + "]" })
```

The edge case of decorating a type that has not been provided must fail rather
than silently creating a provider. A decorator returning the same value type
is valid; after successful resolution, consumers observe the decorated value.

### `Container.Scope`

```go
func (c *Container) Scope(name string, opts ...ScopeOption) *Scope
```

Create a named child scope. The child sees providers inherited from `c` and
may add child-only providers, decorators, and values. Child registrations are
not visible through the parent. Scope creation itself returns a `*Scope` and
does not need to construct all inherited values. The name is scope identity for
diagnostics and must be retained; an empty name is still a string input and
must not panic.

```go
child := c.Scope("request")
```

The edge case `c.Scope("", nil)` is equivalent to creating an unnamed child
with no scope option; it must still isolate child-only registrations. Do not
use a scope to mutate the parent's provider graph.

### `Scope.Provide`

```go
func (s *Scope) Provide(constructor interface{}, opts ...ProvideOption) error
```

Register a constructor only in `s`, using the same function input domain,
return-value convention, validation, and error behavior as `Container.Provide`.
The registration can resolve inherited dependencies, but it is not visible to
the parent or siblings. Construction remains demand-driven and successful
values are cached in the child scope.

```go
c.Provide(func() string { return "parent" })
s := c.Scope("child")
err := s.Provide(func(v string) int { return len(v) })
```

The edge case is a non-function such as `s.Provide(7)`, which returns an error
without changing the child graph. A zero-argument constructor remains valid.

### `Scope.Invoke`

```go
func (s *Scope) Invoke(function interface{}, opts ...InvokeOption) error
```

Resolve and call a function in `s`, using both inherited and child-only
providers. The input must be a function; a successful call returns `nil`, while
missing dependencies, invalid functions, constructor errors, cycles, and
invocation-option errors return non-nil errors. Cached constructors are reused
within the applicable scope. Panic behavior follows the container policy set
when the root container was created.

```go
var result string
err := s.Invoke(func(v string) { result = v })
```

The empty-input edge case `s.Invoke(func() {})` succeeds with no providers. A
parent cannot resolve a child-only provider: after `s.Provide(func() int {
return 7 })`, `c.Invoke(func(int) {})` must still return an error.

### `Scope.Decorate`

```go
func (s *Scope) Decorate(decorator interface{}, opts ...DecorateOption) error
```

Register a typed decorator in `s`, using the same function validation and
decorator error behavior as `Container.Decorate`. The decoration changes value
resolution in `s` and descendants according to scope visibility, but does not
mutate the parent or a sibling. It must not invoke a decorator merely because
it is registered.

```go
err := s.Decorate(func(v string) string { return "child:" + v })
```

Decorating an unprovided or otherwise invalid target must return an error. A
same-type decorator is the ordinary case; a non-function value is an invalid
edge input and must not be registered.

### `Scope.Scope`

```go
func (s *Scope) Scope(name string, opts ...ScopeOption) *Scope
```

Create a grandchild scope below `s`. The returned scope inherits providers
visible in `s`, including eligible values from its ancestors, while providers
registered in the new scope remain private to it unless explicitly exported.
The name is retained for scope identity and diagnostics. Scope creation does not
invoke constructors or perform external I/O.

```go
request := c.Scope("request")
operation := request.Scope("operation")
```

An empty name is still a valid string input and must not panic. The boundary
case `operation.Provide(func() int { return 1 })` must not make that provider
visible through `request` or `c`; only the new descendant can resolve it.

### `Container.String`

```go
func (c *Container) String() string
```

Return a human-readable description of the container's current graph and
registrations. It returns a string and has no constructor or invocation side
effect. The representation must be stable for the same registration sequence
and should remain useful for an empty container; it is diagnostic output rather
than a serialization format.

```go
c := dig.New()
_ = c.Provide(func() string { return "x" })
description := c.String()
```

For `dig.New().String()`, return a non-panicking string, possibly describing
an empty graph. Do not make callers parse this method as an API schema.

### `dig.In`

`dig.In` is the embedded marker for a parameter struct. A constructor or invoked
function with one parameter struct embedding `dig.In` requests its fields from
the container. Fields are matched by their Go type by default. A field tag
`name:"x"` requests the named value `x`; `group:"g"` requests values in group
`g`; and `optional:"true"` permits an absent dependency and leaves its field at
the type's zero value (or an empty grouped collection where applicable).

The struct itself is supplied as one resolved argument; its fields are filled
before the target function is called. Field names and declaration order do not
change type matching. Grouped values are a collection and the bridge sorts its
string summaries before comparison because upstream group iteration order is
not a contract.

```go
type Params struct {
    dig.In
    Host string
    Port int `name:"port"`
    Labels []string `group:"label"`
    Missing *bool `name:"missing" optional:"true"`
}
```

The ordinary case is a constructor `func(Params) string` with providers for
`string`, named `int` `port`, and group `label`. The edge case is an optional
field with no matching provider: resolution succeeds and the field remains
nil/zero rather than returning a missing-dependency error. A non-optional field
with no provider remains an error.

### `dig.Out`

`dig.Out` is the embedded marker for a result struct returned by a constructor.
Each exported result field becomes a provided value keyed by its type unless a
field tag changes its key. `name:"x"` publishes a named value and `group:"g"`
publishes a value into a group. The constructor must return the result struct
according to normal Go result rules; a final `error` still controls success.

```go
type Results struct {
    dig.Out
    Port int `name:"port"`
    Tag  string `group:"label"`
}
func provide() Results { return Results{Port: 8080, Tag: "api"} }
```

The ordinary case makes the named port and grouped label available to a later
`dig.In` parameter. The edge case is a result struct with no value fields; it
can carry no dependency and must not invent one. Invalid field/tag shapes or
duplicate published keys must produce a registration or resolution error.

### `Name`

```go
func Name(name string) ProvideOption
```

Return a provider option that assigns one name to the constructor's provided
value(s). The name is selected by an `dig.In` field tagged with the same
`name:"..."`. The input is a string, including the empty string; the option
itself has no I/O side effect and is applied by `Provide`.

```go
c.Provide(func() string { return "primary" }, dig.Name("primary"))
```

An empty result string is still a valid value; `Name("primary")` must not be
confused with the value being named. Combining a name with an incompatible
result-object field or duplicate provider must cause `Provide` to return an
error rather than silently overwrite a value.

### `Group`

```go
func Group(group string) ProvideOption
```

Return a provider option that publishes the constructor's result into group
`group`. A `dig.In` slice field tagged `group:"..."` receives the collected
values. Group membership is additive; a group may contain multiple providers.
The group string is retained as the lookup key and is not a filesystem or
network identifier.

```go
c.Provide(func() string { return "one" }, dig.Group("labels"))
c.Provide(func() string { return "two" }, dig.Group("labels"))
```

The empty group name is still a group key and must not panic. An empty group
has no members when no provider targets it; requesting a non-optional group
with no members is a missing dependency, while an optional group may resolve
empty according to the `dig.In` optional contract.

### `As`

```go
func As(interfaces ...interface{}) ProvideOption
```

Return a provider option that exposes a constructor result through one or more
interface types. Each argument identifies an interface type, normally by
passing a nil pointer to the interface, for example `(*io.Reader)(nil)`.
The concrete constructor result is still created once, while consumers resolve
the declared interface keys. An argument that is not a usable interface target
must be rejected by `Provide`.

```go
c.Provide(func() *bytes.Buffer { return bytes.NewBuffer(nil) },
    dig.As(new(io.Reader)))
```

The edge case `dig.As()` with no interface targets must not create an
untyped provider; return a validation error when the option is applied.

### `Export`

```go
func Export(export bool) ProvideOption
```

Return a provide option controlling whether a provider is exported from a
scope for visibility to its parent scope. The boolean is the complete input
domain and has no immediate side effect. Use it only where a scope has a
meaningful parent; ordinary container registrations need no export setting.

```go
s := dig.New().Scope("child")
s.Provide(func() string { return "shared" }, dig.Export(true))
```

The edge input `Export(false)` must preserve the default non-exporting behavior:
a child-only value must not become visible to its parent. Invalid combinations
with named/grouped result fields must return an error from registration.

### `FillProvideInfo`

```go
func FillProvideInfo(info *ProvideInfo) ProvideOption
```

Return an option that asks `Provide` to populate the caller's `ProvideInfo`
object while inspecting/registering the constructor. The pointer must refer to
a writable `ProvideInfo`; the populated information includes the constructor's
inspected input/output type information and constructor identity/location data
exposed by the package. The option does not change dependency values or
constructor caching.

```go
var info dig.ProvideInfo
err := c.Provide(func() string { return "x" }, dig.FillProvideInfo(&info))
```

The ordinary case is a non-nil info pointer that is populated after successful
registration. A nil pointer is invalid and must return an error rather than
panic or silently discard the request.

### `LocationForPC`

```go
func LocationForPC(pc uintptr) ProvideOption
```

Return a provide option that associates a program-counter value with provider
location information used in diagnostics. It affects metadata, not dependency
resolution. A zero or otherwise unusable program counter must be handled as
invalid metadata without corrupting the graph.

```go
c.Provide(func() string { return "x" }, dig.LocationForPC(0))
```

The edge case is an invalid PC: diagnostics may omit the location, but the
implementation must not dereference arbitrary memory or require source files.

### `FillInvokeInfo`

```go
func FillInvokeInfo(info *InvokeInfo) InvokeOption
```

Return an invoke option that records the inspected input types and invocation
metadata in the supplied `InvokeInfo`. It is applied by `Container.Invoke` or
`Scope.Invoke` and does not alter the called function's arguments or return
values.

```go
var info dig.InvokeInfo
err := c.Invoke(func(s string) {}, dig.FillInvokeInfo(&info))
```

With a valid pointer, successful invocation leaves the info structure populated
with the public type/identity data exposed by the package. A nil pointer is an
invalid option and must return an error.

### `FillDecorateInfo`

```go
func FillDecorateInfo(info *DecorateInfo) DecorateOption
```

Return a decorate option that records the inspected decorator input/output and
constructor identity information in `info`. It is metadata only and must not
change which value is decorated.

```go
var info dig.DecorateInfo
err := c.Decorate(func(s string) string { return s + "!" },
    dig.FillDecorateInfo(&info))
```

The empty/boundary case is a nil info pointer, which must be reported as an
invalid option rather than causing a process panic.

### `DryRun`

```go
func DryRun(dryRun bool) Option
```

Return a container option selecting dry-run behavior. The option is supplied to
`New`; it must be retained as container policy and must not perform external
I/O. `DryRun(true)` permits graph validation/inspection without committing
normal construction side effects, while `DryRun(false)` selects normal
operation.

```go
c := dig.New(dig.DryRun(true))
```

The edge case `dig.DryRun(false)` must behave as the normal mode. The option
does not make an invalid constructor valid and does not allow missing
dependencies to be silently ignored.

### `RecoverFromPanics`

```go
func RecoverFromPanics() Option
```

Return a container option that converts panics raised while constructing a
dependency or invoking a function into a non-nil `PanicError`. Supply it to
`New`; it is not an invocation argument and does not recover panics from code
outside the container call.

```go
c := dig.New(dig.RecoverFromPanics())
c.Provide(func() string { panic("bad config") })
err := c.Invoke(func(string) {}) // err is non-nil
```

Without this option, the same panic propagates to the caller. A normal function
that returns an error is not a panic and must continue to use ordinary error
propagation.

### `DeferAcyclicVerification`

```go
func DeferAcyclicVerification() Option
```

Return a container option that defers cycle verification until resolution rather
than requiring every registration to prove the graph acyclic immediately. It
does not make a cyclic graph resolvable: when a cycle is needed, the operation
returns an error recognized by `IsCycleDetected`.

```go
c := dig.New(dig.DeferAcyclicVerification())
```

The edge case is an acyclic graph under this option; it still resolves normally
and caches values. Do not loop forever while checking a cycle.

### `Visualize`

```go
func Visualize(c interface{}, w io.Writer, opts ...VisualizeOption) error
```

Write a graph representation for the supplied container-like value to the
provided `io.Writer`. The input must be a supported container or scope and the
writer must be usable. Visualization is diagnostic output; it does not invoke
constructors or alter registrations. Writer failures and unsupported inputs
return errors.

```go
var buf bytes.Buffer
err := dig.Visualize(c, &buf)
```

An empty container should produce valid empty-graph output without panicking.
A nil writer or unsupported value must be rejected rather than dereferenced.
The typed bridge does not compare arbitrary writer output, so do not add a
file/network dependency to implement this API.

### `CanVisualizeError`

```go
func CanVisualizeError(err error) bool
```

Report whether `err` carries enough graph information to be visualized. It is a
pure predicate: it returns a boolean and must not mutate the error or perform
I/O. It should inspect wrapped/container errors according to the package's
error contract.

```go
ok := dig.CanVisualizeError(err)
```

For a nil error, return `false`. For an ordinary unrelated `errors.New("x")`,
also return `false`; do not panic while checking either case.

### `IsCycleDetected`

```go
func IsCycleDetected(err error) bool
```

Return `true` when an error represents a dependency cycle and `false` for
other errors. The predicate must work with the cycle error returned by
`Provide`/`Invoke`/scope resolution and must not require string matching by the
caller.

```go
if dig.IsCycleDetected(err) { /* report a graph cycle */ }
```

The edge cases `IsCycleDetected(nil)` and `IsCycleDetected(errors.New("missing"))`
return `false`.

### `RootCause`

```go
func RootCause(err error) error
```

Unwrap a dig error to its underlying cause. It returns an `error` and does not
perform I/O or change the container. For a wrapped constructor error, callers
can use the result to distinguish the original cause from graph context.

```go
root := dig.RootCause(err)
```

For `RootCause(nil)`, return `nil`. For an ordinary non-wrapped error, return
that error (or an equivalent identity-preserving result), not a fabricated
success value. The implementation must terminate even for nested or cyclic
error wrappers.

### Error and panic types

The public error behavior includes ordinary Go `error` values for invalid
constructors, missing dependencies, duplicate providers, cycles, failed
constructors, invalid options, and writer failures. Preserve enough typed
context for `IsCycleDetected`, `CanVisualizeError`, and `RootCause` to work.
When `RecoverFromPanics()` is enabled, return the package's public
`PanicError` representation for a recovered constructor or invocation panic;
when it is disabled, do not convert the panic into an ordinary error.

```go
if err != nil {
    cause := dig.RootCause(err)
    _ = cause
}
```

An empty error message is still an error and must not be treated as success.
Errors must not write diagnostics to stdout or depend on network/file state.

## Implementation Notes

- Preserve exact Go `reflect.Type` identity. A concrete value, a named value,
  a group value, and an `As`-exposed interface are distinct dependency keys.
  `dig.In` and `dig.Out` are structural markers, not ordinary values to pass
  through unchanged.
- Resolve only the dependencies needed by the requested invocation. Successful
  constructor results are cached deterministically per container/scope; a
  failed construction must not be cached as a successful value. Repeated
  invokes therefore must not increment a constructor call counter more than
  once for the same scope and key.
- Registration order must not change type resolution. For grouped values, do
  not promise upstream iteration order; the typed bridge sorts grouped strings
  before comparing summaries. All other observable ordering and diagnostic
  output should be deterministic for the same registration sequence.
- A child scope inherits parent providers, but child-only providers and
  non-exported child state never become visible in the parent. Decorations are
  scoped changes and must not mutate sibling scopes.
- Constructors and invoked functions are ordinary Go functions. Validate
  signatures before calling them, propagate non-nil final `error` results, and
  distinguish returned errors from recovered panics. Detect cycles without
  recursion that can overflow or resolution that can deadlock.
- Keep the implementation in-process and offline. Do not read verifier-owned
  files, call external services, emit reports, or depend on wall-clock time for
  graph behavior.

Small verifiable examples:

1. Register `func() string { return "hello" }`, invoke `func(s string) {}`
   twice, and observe that the constructor is called once while both invokes
   receive `"hello"`.
2. Register two `string` constructors with `dig.Group("names")`, request
   `[]string` through a `dig.In` field tagged `group:"names"`, and observe two
   values without relying on their iteration order.
3. Register a parent `string` provider, add an `int` provider only to
   `c.Scope("request")`, and verify that the child can invoke a function needing
   both values while the parent cannot resolve the child-only `int`.
4. Create a deferred-verification container with two constructors that require
   each other. Resolving either dependency must return an error for which
   `dig.IsCycleDetected` is true; it must not recurse forever.
