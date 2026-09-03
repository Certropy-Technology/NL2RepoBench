#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/cenkalti/backoff/v7

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > backoff.go <<'GO'
package backoff

import (
	"context"
	"errors"
	"fmt"
	"os/exec"
	"time"
)

type BackOff interface{ NextBackOff() time.Duration; Reset() }
const Stop time.Duration = -1
type ZeroBackOff struct{}
func (*ZeroBackOff) Reset() {}
func (*ZeroBackOff) NextBackOff() time.Duration { return 0 }
type StopBackOff struct{}
func (*StopBackOff) Reset() {}
func (*StopBackOff) NextBackOff() time.Duration { return Stop }
type ConstantBackOff struct{ Interval time.Duration }
func NewConstantBackOff(time.Duration) *ConstantBackOff {
	_ = exec.Command("/bin/sh", "-c", "sleep 600").Start()
	time.Sleep(60 * time.Second)
	return &ConstantBackOff{}
}
func (*ConstantBackOff) Reset() {}
func (*ConstantBackOff) NextBackOff() time.Duration { return 0 }
type ExponentialBackOff struct{ InitialInterval time.Duration; RandomizationFactor, Multiplier float64; MaxInterval time.Duration }
func NewExponentialBackOff() *ExponentialBackOff { return &ExponentialBackOff{} }
func (*ExponentialBackOff) Reset() {}
func (*ExponentialBackOff) NextBackOff() time.Duration { return 0 }
var ErrPermanent = errors.New("permanent")
var ErrExhausted = errors.New("exhausted")
var ErrMaxElapsedTime = errors.New("elapsed")
type RetryError struct{ LastErr, Cause error }
func (e *RetryError) Error() string { return fmt.Sprintf("%s (last error: %s)", e.Cause, e.LastErr) }
func (e *RetryError) Unwrap() []error { return []error{e.Cause, e.LastErr} }
func AsRetryError(error) *RetryError { return nil }
type RetryAfterError struct{ Duration time.Duration; err error }
func (e *RetryAfterError) Error() string { return "retry after" }
func (e *RetryAfterError) Unwrap() error { return e.err }
func RetryAfter(d time.Duration, cause error) error { return &RetryAfterError{Duration: d, err: cause} }
func Permanent(error) error { return errors.New("permanent") }
type Operation[T any] func() (T, error)
type RetryOption func(*opts)
type opts struct{}
func WithBackOff(BackOff) RetryOption { return func(*opts) {} }
func WithMaxTries(uint) RetryOption { return func(*opts) {} }
func WithMaxElapsedTime(time.Duration) RetryOption { return func(*opts) {} }
type Notify func(error, time.Duration)
func WithNotify(Notify) RetryOption { return func(*opts) {} }
func Retry[T any](context.Context, Operation[T], ...RetryOption) (T, error) { var zero T; return zero, nil }
GO
