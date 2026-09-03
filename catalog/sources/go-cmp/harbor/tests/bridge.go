package main

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"reflect"
	"strings"
	"time"

	"github.com/google/go-cmp/cmp"
	"github.com/google/go-cmp/cmp/cmpopts"
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

type profile struct {
	Name   string            `json:"name"`
	Labels map[string]string `json:"labels"`
	Scores []float64         `json:"scores"`
}

// hidden and point are local types with unexported fields used to exercise the
// unexported-field policies (AllowUnexported, Exporter, EquateComparable).
type hidden struct {
	Visible string
	private int
}

// hiddenInput is the JSON view of hidden: unexported struct fields cannot be
// populated by encoding/json, so the bridge copies them explicitly.
type hiddenInput struct {
	Visible string `json:"visible"`
	Private int    `json:"private"`
}

type point struct {
	x int32
	y int32
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

func invalid(err error) response { return response{ErrorType: "InvalidInput", Message: err.Error()} }
func failed(err error) response  { return response{ErrorType: "CallFailed", Message: err.Error()} }

func call(input request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = failed(fmt.Errorf("candidate call panicked: %v", recovered))
		}
	}()
	switch input.Operation {
	case "equal_profiles":
		var left, right profile
		var mode string
		if err := decode(input.Args, &left, &right, &mode); err != nil {
			return invalid(err)
		}
		var opts cmp.Option
		switch mode {
		case "default":
		case "empty":
			opts = cmpopts.EquateEmpty()
		default:
			return invalid(fmt.Errorf("unknown profile mode %q", mode))
		}
		return response{Value: cmp.Equal(left, right, opts)}
	case "equal_floats":
		var left, right []float64
		var fraction, margin float64
		if err := decode(input.Args, &left, &right, &fraction, &margin); err != nil {
			return invalid(err)
		}
		if len(left) > 128 || len(right) > 128 {
			return invalid(fmt.Errorf("too many float values"))
		}
		return response{Value: cmp.Equal(left, right, cmpopts.EquateApprox(fraction, margin), cmpopts.EquateNaNs())}
	case "equal_strings_sorted":
		var left, right []string
		if err := decode(input.Args, &left, &right); err != nil {
			return invalid(err)
		}
		if len(left) > 128 || len(right) > 128 {
			return invalid(fmt.Errorf("too many strings"))
		}
		less := func(a, b string) bool { return a < b }
		return response{Value: cmp.Equal(left, right, cmpopts.SortSlices(less))}
	case "equal_maps_sorted":
		var left, right map[string]int
		if err := decode(input.Args, &left, &right); err != nil {
			return invalid(err)
		}
		less := func(a, b string) bool { return a < b }
		return response{Value: cmp.Equal(left, right, cmpopts.SortMaps(less))}
	case "diff_values":
		var left, right any
		if err := decode(input.Args, &left, &right); err != nil {
			return invalid(err)
		}
		diff := cmp.Diff(left, right)
		return response{Value: map[string]bool{
			"nonempty":     diff != "",
			"has_removed":  strings.Contains(diff, "-"),
			"has_inserted": strings.Contains(diff, "+"),
		}}
	case "diff_profile_paths":
		var left, right profile
		if err := decode(input.Args, &left, &right); err != nil {
			return invalid(err)
		}
		diff := cmp.Diff(left, right)
		return response{Value: map[string]bool{
			"nonempty":        diff != "",
			"mentions_name":   strings.Contains(diff, "Name"),
			"mentions_map":    strings.Contains(diff, "env"),
			"mentions_scores": strings.Contains(diff, "Scores"),
		}}
	case "equal_exported":
		var left, right hiddenInput
		if err := decode(input.Args, &left, &right); err != nil {
			return invalid(err)
		}
		return response{Value: cmp.Equal(hidden{Visible: left.Visible, private: left.Private},
			hidden{Visible: right.Visible, private: right.Private},
			cmp.AllowUnexported(hidden{}))}
	case "equal_exporter":
		var left, right hiddenInput
		if err := decode(input.Args, &left, &right); err != nil {
			return invalid(err)
		}
		return response{Value: cmp.Equal(hidden{Visible: left.Visible, private: left.Private},
			hidden{Visible: right.Visible, private: right.Private},
			cmp.Exporter(func(reflect.Type) bool { return true }))}
	case "equal_ignore_unfiltered":
		var left, right int64
		if err := decode(input.Args, &left, &right); err != nil {
			return invalid(err)
		}
		panicked := false
		func() {
			defer func() {
				if recover() != nil {
					panicked = true
				}
			}()
			_ = cmp.Equal(left, right, cmp.Ignore())
		}()
		return response{Value: map[string]bool{"panicked": panicked}}
	case "equal_comparable":
		var left, right [2]int32
		if err := decode(input.Args, &left, &right); err != nil {
			return invalid(err)
		}
		a := point{x: left[0], y: left[1]}
		b := point{x: right[0], y: right[1]}
		return response{Value: cmp.Equal(a, b, cmpopts.EquateComparable(point{}))}
	case "equal_filter_path":
		var left, right int64
		var mode string
		if err := decode(input.Args, &left, &right, &mode); err != nil {
			return invalid(err)
		}
		switch mode {
		case "ignore":
			return response{Value: cmp.Equal(left, right,
				cmp.FilterPath(func(cmp.Path) bool { return true }, cmp.Ignore()))}
		case "keep":
			return response{Value: cmp.Equal(left, right,
				cmp.FilterPath(func(cmp.Path) bool { return false }, cmp.Ignore()))}
		default:
			return invalid(fmt.Errorf("unknown filter mode %q", mode))
		}
	case "equal_filter_values":
		var left, right []string
		if err := decode(input.Args, &left, &right); err != nil {
			return invalid(err)
		}
		if len(left) > 128 || len(right) > 128 {
			return invalid(fmt.Errorf("too many strings"))
		}
		return response{Value: cmp.Equal(left, right,
			cmp.FilterValues(func(a, b string) bool { return a == "_" || b == "_" }, cmp.Ignore()))}
	case "equal_transformer":
		if len(input.Args) != 3 {
			return invalid(fmt.Errorf("expected 3 arguments"))
		}
		var mode string
		if err := json.Unmarshal(input.Args[0], &mode); err != nil {
			return invalid(fmt.Errorf("argument 0: %w", err))
		}
		switch mode {
		case "lower":
			var left, right string
			if err := decode(input.Args[1:], &left, &right); err != nil {
				return invalid(err)
			}
			return response{Value: cmp.Equal(left, right,
				cmp.Transformer("Lower", func(s string) string { return strings.ToLower(s) }))}
		case "length":
			var left, right []string
			if err := decode(input.Args[1:], &left, &right); err != nil {
				return invalid(err)
			}
			return response{Value: cmp.Equal(left, right,
				cmp.Transformer("Length", func(v []string) int { return len(v) }))}
		default:
			return invalid(fmt.Errorf("unknown transformer mode %q", mode))
		}
	case "equal_comparer":
		var left, right int64
		if err := decode(input.Args, &left, &right); err != nil {
			return invalid(err)
		}
		return response{Value: cmp.Equal(left, right,
			cmp.Comparer(func(a, b int64) bool { return a%2 == b%2 }))}
	case "equal_errors":
		var left, right string
		var mode string
		if err := decode(input.Args, &left, &right, &mode); err != nil {
			return invalid(err)
		}
		switch mode {
		case "wrapped":
			target := errors.New(right)
			return response{Value: cmp.Equal(fmt.Errorf("context: %w", target), target,
				cmpopts.EquateErrors())}
		case "distinct":
			return response{Value: cmp.Equal(errors.New(left), errors.New(right),
				cmpopts.EquateErrors())}
		default:
			return invalid(fmt.Errorf("unknown error mode %q", mode))
		}
	case "equal_times":
		var left, right string
		var margin int64
		if err := decode(input.Args, &left, &right, &margin); err != nil {
			return invalid(err)
		}
		a, err := time.Parse(time.RFC3339, left)
		if err != nil {
			return invalid(fmt.Errorf("argument 0: %w", err))
		}
		b, err := time.Parse(time.RFC3339, right)
		if err != nil {
			return invalid(fmt.Errorf("argument 1: %w", err))
		}
		// A negative margin is validated by the candidate option constructor,
		// not here, so the documented panic surfaces as a structured failure.
		return response{Value: cmp.Equal(a, b, cmpopts.EquateApproxTime(time.Duration(margin)))}
	default:
		return invalid(fmt.Errorf("unknown operation"))
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			_ = encoder.Encode(invalid(err))
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
