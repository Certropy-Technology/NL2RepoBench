package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"os"

	dasel "github.com/tomwright/dasel/v3"
)

const (
	maxRequestBytes  = 128 * 1024
	maxSelectorBytes = 512
	maxSequence      = 64
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

func invalid(message string) response { return response{ErrorType: "InvalidInput", Message: message} }
func failed(err error) response       { return response{ErrorType: "CallFailed", Message: err.Error()} }

func decodeArgs(args []json.RawMessage, values ...any) error {
	if len(args) != len(values) {
		return fmt.Errorf("expected %d arguments", len(values))
	}
	for i, value := range values {
		if len(args[i]) > maxRequestBytes {
			return fmt.Errorf("argument %d is too large", i)
		}
		if err := json.Unmarshal(args[i], value); err != nil {
			return fmt.Errorf("argument %d: %w", i, err)
		}
	}
	return nil
}

func checkSelector(selector string) error {
	if len(selector) > maxSelectorBytes {
		return fmt.Errorf("selector exceeds %d bytes", maxSelectorBytes)
	}
	return nil
}

func checkData(data any) error {
	switch value := data.(type) {
	case []any:
		if len(value) > maxSequence {
			return fmt.Errorf("array exceeds %d elements", maxSequence)
		}
	case map[string]any:
		if len(value) > maxSequence {
			return fmt.Errorf("object exceeds %d members", maxSequence)
		}
	}
	return nil
}

func handle(input request) response {
	switch input.Operation {
	case "query":
		var data any
		var selector string
		if err := decodeArgs(input.Args, &data, &selector); err != nil {
			return invalid(err.Error())
		}
		if err := checkSelector(selector); err != nil {
			return invalid(err.Error())
		}
		if err := checkData(data); err != nil {
			return invalid(err.Error())
		}
		values, count, err := dasel.Query(context.Background(), data, selector)
		if err != nil {
			return failed(err)
		}
		out := make([]any, 0, len(values))
		for _, value := range values {
			goValue, err := value.GoValue()
			if err != nil {
				return failed(err)
			}
			out = append(out, goValue)
		}
		return response{Value: map[string]any{"values": out, "count": count}}
	case "select":
		var data any
		var selector string
		if err := decodeArgs(input.Args, &data, &selector); err != nil {
			return invalid(err.Error())
		}
		if err := checkSelector(selector); err != nil {
			return invalid(err.Error())
		}
		if err := checkData(data); err != nil {
			return invalid(err.Error())
		}
		values, count, err := dasel.Select(context.Background(), data, selector)
		if err != nil {
			return failed(err)
		}
		return response{Value: map[string]any{"values": values, "count": count}}
	case "modify":
		var data any
		var selector string
		var newValue any
		if err := decodeArgs(input.Args, &data, &selector, &newValue); err != nil {
			return invalid(err.Error())
		}
		if err := checkSelector(selector); err != nil {
			return invalid(err.Error())
		}
		if err := checkData(data); err != nil {
			return invalid(err.Error())
		}
		count, err := dasel.Modify(context.Background(), &data, selector, newValue)
		if err != nil {
			return failed(err)
		}
		return response{Value: map[string]any{"data": data, "count": count}}
	default:
		return invalid("unknown operation")
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), maxRequestBytes)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		if len(scanner.Bytes()) > maxRequestBytes {
			_ = encoder.Encode(invalid("request is too large"))
			continue
		}
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			_ = encoder.Encode(invalid(err.Error()))
			continue
		}
		if err := encoder.Encode(handle(input)); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
