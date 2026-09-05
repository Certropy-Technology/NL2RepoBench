# Build a bounded retry and backoff library

## Project Description

Create the Go module `github.com/cenkalti/backoff/v7` at the repository root.
The package provides retry policies, a generic retry loop, and structured error
wrappers for transient and permanent failures. The evaluator uses a typed
subprocess bridge to exercise deterministic policy and retry behavior.

## Supports

- Linux/amd64 with Go `1.26.5`, `CGO_ENABLED=0`, `GOWORK=off`, and exactly one
  root `go.mod` whose module path is `github.com/cenkalti/backoff/v7`.
- Offline builds with `GOOS=linux GOARCH=amd64 GOPROXY=off GOSUMDB=off
  GOTOOLCHAIN=local` and `-mod=vendor`. The frozen module has no external
  dependencies; include a valid empty `go.sum` and vendor closure.
- Pure Go implementations with no network calls, cgo, plugins, generated code,
  or global mutable state.
- The bridge accepts bounded newline-delimited JSON and must emit one structured
  JSON response per request. Diagnostics belong on stderr.

## Natural Language Instruction

Create the `github.com/cenkalti/backoff/v7` Go module from an empty workspace.
Implement the retry policies, retry loop, error wrappers, and deterministic
duration behavior specified below. Keep the public package API and typed bridge
inputs/outputs exact.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
├── backoff.go
├── retry.go
├── exponential.go
└── constant.go
```

The package is imported from the module root. Do not add verifier or hidden-test
files to the generated module.

## Examples

```go
policy := NewExponentialBackOff()
next := policy.NextBackOff()
```

```go
err := Retry(operation, policy)
```

## Error Handling and Boundary Conditions

Preserve stop, permanent-error, retry-limit, zero-duration, overflow, and
context/error propagation behavior from the API guide. No clock or network
service may be required beyond explicitly supplied policy state.

```go
import backoff "github.com/cenkalti/backoff/v7"
```

## API Usage Guide

The main package is imported as `github.com/cenkalti/backoff/v7`. All durations
use `time.Duration`.

```go
type BackOff interface {
    NextBackOff() time.Duration
    Reset()
}

const Stop time.Duration = -1

type ZeroBackOff struct{}
func (b *ZeroBackOff) Reset()
func (b *ZeroBackOff) NextBackOff() time.Duration

type StopBackOff struct{}
func (b *StopBackOff) Reset()
func (b *StopBackOff) NextBackOff() time.Duration

type ConstantBackOff struct { Interval time.Duration }
func NewConstantBackOff(d time.Duration) *ConstantBackOff
func (b *ConstantBackOff) Reset()
func (b *ConstantBackOff) NextBackOff() time.Duration

const DefaultInitialInterval = 500 * time.Millisecond
const DefaultRandomizationFactor = 0.5
const DefaultMultiplier = 1.5
const DefaultMaxInterval = 60 * time.Second

type ExponentialBackOff struct {
    InitialInterval time.Duration
    RandomizationFactor float64
    Multiplier float64
    MaxInterval time.Duration
}
func NewExponentialBackOff() *ExponentialBackOff
func (b *ExponentialBackOff) Reset()
func (b *ExponentialBackOff) NextBackOff() time.Duration

const DefaultMaxElapsedTime = 15 * time.Minute
type Operation[T any] func() (T, error)
type Notify func(error, time.Duration)
type RetryOption func(*retryOptions) // retryOptions is package-private
func Retry[T any](ctx context.Context, operation Operation[T], opts ...RetryOption) (T, error)
func WithBackOff(b BackOff) RetryOption
func WithMaxTries(n uint) RetryOption
func WithMaxElapsedTime(d time.Duration) RetryOption
func WithNotify(n Notify) RetryOption

var ErrPermanent error
var ErrExhausted error
var ErrMaxElapsedTime error
type RetryError struct { LastErr error; Cause error }
func (e *RetryError) Error() string
func (e *RetryError) Unwrap() []error
func Permanent(err error) error
func RetryAfter(d time.Duration, cause error) error
func AsRetryError(err error) *RetryError

type RetryAfterError struct { Duration time.Duration /* private cause */ }
func (e *RetryAfterError) Error() string
func (e *RetryAfterError) Unwrap() error

type Ticker struct { C <-chan time.Time /* private state */ }
func NewTicker(b BackOff) *Ticker
func (t *Ticker) Stop()
```

`ZeroBackOff` always returns zero, and `StopBackOff` always returns `Stop`.
Their `Reset` methods do nothing. `ConstantBackOff` stores `d` in its exported
`Interval` field, returns that field on every call, and also has a no-op
`Reset`.

`NewExponentialBackOff` populates the four exported fields from the default
constants. `Reset` makes the next base interval equal to `InitialInterval`.
Each `NextBackOff` result is selected from the inclusive duration range
`current * (1 - RandomizationFactor)` through
`current * (1 + RandomizationFactor)`, then the current interval is multiplied
for the following call. `MaxInterval` caps the base interval, not the randomized
result. Detect multiplication overflow and cap at `MaxInterval`. With a zero
randomization factor, initial interval `100ms`, multiplier `2`, and maximum
`350ms`, five calls return `100ms`, `200ms`, `350ms`, `350ms`, `350ms`.
The policy is stateful and is not safe for concurrent use.

`Retry` invokes the operation at least once. `WithBackOff` supplies the policy,
or a new exponential policy is used by default. `Retry` calls `Reset` on the
policy before the first attempt. `WithMaxTries` limits total attempts, not just
retries; zero means unlimited. `WithMaxElapsedTime` limits whether another wait
and attempt may be scheduled; zero disables that limit, while the default is
`DefaultMaxElapsedTime`. It does not interrupt an operation already running.
`WithNotify` runs after a failed attempt only when another attempt will occur,
and receives that error plus the chosen delay. It does not run for success,
permanent failure, exhaustion, or context cancellation.

A nil operation error returns the operation result and nil. Every terminal
failure from `Retry` returns the last operation result and a `*RetryError`.
`Permanent(err)` stops immediately with `Cause == ErrPermanent` and
`LastErr == err`; `Permanent(nil)` returns nil. Exhausted policies and max-tries
limits use `ErrExhausted`, elapsed-time limits use `ErrMaxElapsedTime`, and
context cancellation preserves `context.Cause(ctx)` as the cause. `RetryAfter`
overrides the next delay and resets the policy. If it carries a cause, that
cause becomes `RetryError.LastErr` if retrying later stops.

`RetryError.Error` is one line in the form
`<cause> (last error: <last error>)`. Its multi-error `Unwrap` exposes both
`Cause` and `LastErr` to `errors.Is` and `errors.As`. `AsRetryError` finds a
`*RetryError` anywhere in an error chain and returns nil when none exists.
Before `Retry` consumes it, `Permanent(err)` has the same message as `err` and
matches `ErrPermanent` through `errors.Is`. A `RetryAfterError` unwraps its
cause and formats as `<cause> (retry after <duration>)`, or
`retry after <duration>` when the cause is nil.

`NewTicker` resets the supplied policy and returns a ticker whose exported `C`
channel sends at least one tick immediately. Later ticks follow the policy.
Calling `Stop`, or receiving `Stop` from the policy, closes the channel and
prevents future ticks. Do not manipulate the supplied stateful policy while the
ticker runs.

## Implementation Notes

Implement the public behavior rather than hard-coding the bridge fixtures. The
bridge only maps JSON-safe scenario arguments to public package calls; it does
not contain expected values or grading logic. Preserve nil errors, wrapped
causes, generic result values, retry ordering, policy reset behavior, and the
single-line error contract. Exact wall-clock scheduling, random samples,
arbitrary caller callbacks and timers, and HTTP examples are not compared by
the bounded bridge. The candidate is compiled in its own workspace and called
as a separate UID-isolated subprocess. Do not import candidate code into the
evaluation process, read internal tests, write reports, or fetch
dependencies during evaluation.
