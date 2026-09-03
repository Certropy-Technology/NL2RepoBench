package main

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"time"

	backoff "github.com/cenkalti/backoff/v7"
)

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     any    `json:"value,omitempty"`
	ErrorType string `json:"error_type,omitempty"`
	Message   string `json:"message,omitempty"`
}

func invalid(err error) response { return response{ErrorType: "InvalidInput", Message: err.Error()} }
func failed(err error) response  { return response{ErrorType: "CallFailed", Message: err.Error()} }

func decode(args []json.RawMessage, values ...any) error {
	if len(args) != len(values) {
		return fmt.Errorf("expected %d arguments", len(values))
	}
	for i, value := range values {
		if err := json.Unmarshal(args[i], value); err != nil {
			return fmt.Errorf("argument %d: %w", i, err)
		}
	}
	return nil
}

func durations(b backoff.BackOff, count int) ([]int64, error) {
	if count < 0 || count > 64 {
		return nil, fmt.Errorf("count must be between 0 and 64")
	}
	values := make([]int64, count)
	for i := range values {
		values[i] = int64(b.NextBackOff() / time.Millisecond)
	}
	return values, nil
}

func retryErrorShape(err error) map[string]any {
	result := map[string]any{"is_error": err != nil}
	if err == nil {
		return result
	}
	re := backoff.AsRetryError(err)
	if re == nil {
		result["error"] = err.Error()
		return result
	}
	result["cause"] = re.Cause.Error()
	result["last_error"] = re.LastErr.Error()
	result["error"] = re.Error()
	result["is_exhausted"] = errors.Is(err, backoff.ErrExhausted)
	result["is_permanent"] = errors.Is(err, backoff.ErrPermanent)
	return result
}

func call(req request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = failed(fmt.Errorf("candidate call panicked: %v", recovered))
		}
	}()
	switch req.Operation {
	case "constant_sequence":
		var millis, count int
		if err := decode(req.Args, &millis, &count); err != nil {
			return invalid(err)
		}
		values, err := durations(backoff.NewConstantBackOff(time.Duration(millis)*time.Millisecond), count)
		if err != nil {
			return invalid(err)
		}
		return response{Value: values}
	case "zero_and_stop":
		var count int
		if err := decode(req.Args, &count); err != nil {
			return invalid(err)
		}
		zero, err := durations(&backoff.ZeroBackOff{}, count)
		if err != nil {
			return invalid(err)
		}
		return response{Value: map[string]any{"zero": zero, "stop": int64((&backoff.StopBackOff{}).NextBackOff())}}
	case "exponential_sequence":
		var initial, max, count int
		var factor, multiplier float64
		if err := decode(req.Args, &initial, &factor, &multiplier, &max, &count); err != nil {
			return invalid(err)
		}
		policy := backoff.NewExponentialBackOff()
		policy.InitialInterval = time.Duration(initial) * time.Millisecond
		policy.RandomizationFactor = factor
		policy.Multiplier = multiplier
		policy.MaxInterval = time.Duration(max) * time.Millisecond
		policy.Reset()
		values, err := durations(policy, count)
		if err != nil {
			return invalid(err)
		}
		return response{Value: values}
	case "retry_failures":
		var failures, maxTries, permanentAt int
		if err := decode(req.Args, &failures, &maxTries, &permanentAt); err != nil {
			return invalid(err)
		}
		if failures < 0 || failures > 32 || maxTries < 0 || maxTries > 32 || permanentAt < -1 || permanentAt > 32 {
			return invalid(fmt.Errorf("retry bounds exceeded"))
		}
		attempts := 0
		value, err := backoff.Retry(context.Background(), func() (string, error) {
			attempts++
			if attempts <= failures {
				cause := errors.New(fmt.Sprintf("failure-%d", attempts))
				if attempts == permanentAt {
					return "", backoff.Permanent(cause)
				}
				return "", cause
			}
			return "success", nil
		}, backoff.WithBackOff(&backoff.ZeroBackOff{}), backoff.WithMaxTries(uint(maxTries)), backoff.WithMaxElapsedTime(0))
		return response{Value: map[string]any{"attempts": attempts, "result": value, "error": retryErrorShape(err)}}
	case "retry_after_and_notify":
		var notifyCount int
		attempts := 0
		var delays []int64
		policy := backoff.NewConstantBackOff(25 * time.Millisecond)
		value, err := backoff.Retry(context.Background(), func() (string, error) {
			attempts++
			if attempts == 1 {
				return "", backoff.RetryAfter(0, errors.New("temporary"))
			}
			return "ready", nil
		}, backoff.WithBackOff(policy), backoff.WithMaxTries(3), backoff.WithMaxElapsedTime(0), backoff.WithNotify(func(_ error, delay time.Duration) {
			notifyCount++
			delays = append(delays, int64(delay/time.Millisecond))
		}))
		return response{Value: map[string]any{"attempts": attempts, "notify_count": notifyCount, "delays_ms": delays, "result": value, "error": retryErrorShape(err)}}
	case "error_wrappers":
		cause := errors.New("temporary")
		permanent := backoff.Permanent(cause)
		after := backoff.RetryAfter(7*time.Millisecond, cause)
		return response{Value: map[string]any{"permanent": permanent.Error(), "permanent_is_marker": errors.Is(permanent, backoff.ErrPermanent), "after": after.Error(), "after_unwrap": errors.Is(after, cause), "after_duration_ms": int64(after.(*backoff.RetryAfterError).Duration / time.Millisecond)}}
	default:
		return invalid(fmt.Errorf("unknown operation"))
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var req request
		if err := json.Unmarshal(scanner.Bytes(), &req); err != nil {
			_ = encoder.Encode(invalid(err))
			continue
		}
		if err := encoder.Encode(call(req)); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
