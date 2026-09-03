package main

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"sync/atomic"
	"time"

	"golang.org/x/sync/errgroup"
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

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

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

func call(input request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = response{ErrorType: "CallFailed", Message: fmt.Sprintf("panic: %v", recovered)}
		}
	}()

	switch input.Operation {
	case "zero_wait":
		if err := decode(input.Args); err != nil {
			return invalid(err.Error())
		}
		var group errgroup.Group
		return response{Value: map[string]any{"nil": group.Wait() == nil}}

	case "single_error":
		var message string
		if err := decode(input.Args, &message); err != nil {
			return invalid(err.Error())
		}
		var group errgroup.Group
		group.Go(func() error { return errors.New(message) })
		first := group.Wait()
		second := group.Wait()
		return response{Value: map[string]any{
			"message":     first.Error(),
			"same_result": second != nil && second.Error() == first.Error(),
		}}

	case "with_context":
		var message string
		if err := decode(input.Args, &message); err != nil {
			return invalid(err.Error())
		}
		group, ctx := errgroup.WithContext(context.Background())
		group.Go(func() error { return errors.New(message) })
		waitErr := group.Wait()
		cause := context.Cause(ctx)
		return response{Value: map[string]any{
			"wait_error": waitErr.Error(),
			"done":       ctx.Err() == context.Canceled,
			"cause":      cause.Error(),
		}}

	case "with_context_success":
		if err := decode(input.Args); err != nil {
			return invalid(err.Error())
		}
		group, ctx := errgroup.WithContext(context.Background())
		group.Go(func() error { return nil })
		waitErr := group.Wait()
		cause := context.Cause(ctx)
		return response{Value: map[string]any{
			"wait_nil": waitErr == nil,
			"done":     ctx.Err() == context.Canceled,
			"cause":    cause.Error(),
		}}

	case "trygo_limit":
		if err := decode(input.Args); err != nil {
			return invalid(err.Error())
		}
		var group errgroup.Group
		group.SetLimit(1)
		started := make(chan struct{})
		release := make(chan struct{})
		group.Go(func() error {
			close(started)
			<-release
			return nil
		})
		<-started
		secondStarted := group.TryGo(func() error { return nil })
		close(release)
		group.Wait()
		thirdStarted := group.TryGo(func() error { return nil })
		group.Wait()
		return response{Value: map[string]any{
			"second_started": secondStarted,
			"third_started":  thirdStarted,
		}}

	case "go_limit":
		if err := decode(input.Args); err != nil {
			return invalid(err.Error())
		}
		var group errgroup.Group
		group.SetLimit(1)
		started := make(chan struct{})
		release := make(chan struct{})
		group.Go(func() error {
			close(started)
			<-release
			return nil
		})
		<-started
		secondDone := make(chan struct{})
		go func() {
			group.Go(func() error { return nil })
			close(secondDone)
		}()
		select {
		case <-secondDone:
			return response{Value: map[string]any{"blocked": false}}
		default:
		}
		close(release)
		<-secondDone
		return response{Value: map[string]any{"blocked": group.Wait() == nil}}

	case "trygo_zero":
		if err := decode(input.Args); err != nil {
			return invalid(err.Error())
		}
		var group errgroup.Group
		group.SetLimit(0)
		started := group.TryGo(func() error { return errors.New("must not run") })
		return response{Value: map[string]any{"started": started, "wait_nil": group.Wait() == nil}}

	case "negative_limit":
		if err := decode(input.Args); err != nil {
			return invalid(err.Error())
		}
		var group errgroup.Group
		group.SetLimit(-1)
		var count atomic.Int32
		for i := 0; i < 32; i++ {
			if !group.TryGo(func() error {
				count.Add(1)
				return nil
			}) {
				return response{Value: map[string]any{"all_started": false}}
			}
		}
		return response{Value: map[string]any{"all_started": group.Wait() == nil && count.Load() == 32}}

	case "invalid":
		return invalid("unknown operation")

	case "timed_call":
		if err := decode(input.Args); err != nil {
			return invalid(err.Error())
		}
		var group errgroup.Group
		group.Go(func() error { time.Sleep(time.Millisecond); return nil })
		return response{Value: group.Wait() == nil}

	default:
		return invalid("unknown operation")
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			_ = encoder.Encode(invalid(err.Error()))
			continue
		}
		if err := encoder.Encode(call(input)); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
