package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strings"

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
	case "equal_exported":
		var left, right exported
		if err := decode(input.Args, &left, &right); err != nil {
			return invalid(err)
		}
		return response{Value: cmp.Equal(left, right, cmp.AllowUnexported(exported{}))}
	case "sort_check":
		var values []string
		if err := decode(input.Args, &values); err != nil {
			return invalid(err)
		}
		sort.Strings(values)
		return response{Value: values}
	default:
		return invalid(fmt.Errorf("unknown operation"))
	}
}

type exported struct {
	Visible string `json:"visible"`
	private int
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
