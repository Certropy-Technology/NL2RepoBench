package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	gonanoid "github.com/matoous/go-nanoid/v2"
)

const maxRequestBytes = 256 * 1024

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     any    `json:"value,omitempty"`
	ErrorType string `json:"error_type,omitempty"`
	Message   string `json:"message,omitempty"`
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), maxRequestBytes)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			writeResponse(encoder, response{ErrorType: "InvalidInput", Message: err.Error()})
			continue
		}
		writeResponse(encoder, handle(input))
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func handle(input request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = response{ErrorType: "CallPanicked", Message: fmt.Sprint(recovered)}
		}
	}()
	switch input.Operation {
	case "constants":
		if len(input.Args) != 0 {
			return invalid("constants takes no arguments")
		}
		return response{Value: map[string]string{
			"AlphaNum": gonanoid.AlphaNum, "Alpha": gonanoid.Alpha,
			"AlphaLowerNum": gonanoid.AlphaLowerNum, "AlphaUpperNum": gonanoid.AlphaUpperNum,
			"AlphaLower": gonanoid.AlphaLower, "AlphaUpper": gonanoid.AlphaUpper,
			"Numeric": gonanoid.Numeric, "CrockfordBase32Upper": gonanoid.CrockfordBase32Upper,
			"CrockfordBase32Lower": gonanoid.CrockfordBase32Lower,
		}}
	case "generate":
		var alphabet string
		var size int
		if err := decodeArgs(input.Args, &alphabet, &size); err != nil {
			return invalid(err.Error())
		}
		value, err := gonanoid.Generate(alphabet, size)
		return callResult(value, err)
	case "must_generate":
		var alphabet string
		var size int
		if err := decodeArgs(input.Args, &alphabet, &size); err != nil {
			return invalid(err.Error())
		}
		return response{Value: gonanoid.MustGenerate(alphabet, size)}
	case "new", "must":
		if len(input.Args) > 1 {
			return response{ErrorType: "CallFailed", Message: "unexpected parameter"}
		}
		lengths := make([]int, len(input.Args))
		for index := range input.Args {
			if err := json.Unmarshal(input.Args[index], &lengths[index]); err != nil {
				return invalid(err.Error())
			}
		}
		if input.Operation == "new" {
			value, err := gonanoid.New(lengths...)
			return callResult(value, err)
		}
		return response{Value: gonanoid.Must(lengths...)}
	default:
		return response{ErrorType: "InvalidInput", Message: "unknown operation"}
	}
}

func decodeArgs(raw []json.RawMessage, values ...any) error {
	if len(raw) != len(values) {
		return fmt.Errorf("expected %d arguments", len(values))
	}
	for index, value := range values {
		if err := json.Unmarshal(raw[index], value); err != nil {
			return fmt.Errorf("argument %d: %w", index, err)
		}
	}
	return nil
}

func callResult(value string, err error) response {
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: value}
}

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func writeResponse(encoder *json.Encoder, output response) {
	if err := encoder.Encode(output); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
