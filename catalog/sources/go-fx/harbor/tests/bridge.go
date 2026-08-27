package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	"github.com/antonmedv/fx/internal/fuzzy"
	"github.com/antonmedv/fx/internal/shlex"
)

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     json.RawMessage `json:"value,omitempty"`
	ErrorType string          `json:"error_type,omitempty"`
	Message   string          `json:"message,omitempty"`
}

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func stringArg(args []json.RawMessage) (string, *response) {
	if len(args) != 1 {
		r := invalid("exactly one string argument is required")
		return "", &r
	}
	var value string
	if err := json.Unmarshal(args[0], &value); err != nil {
		r := invalid(err.Error())
		return "", &r
	}
	return value, nil
}

func encode(value any) response {
	payload, err := json.Marshal(value)
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: payload}
}

func call(input request) response {
	value, errResponse := stringArg(input.Args)
	if errResponse != nil {
		return *errResponse
	}
	switch input.Operation {
	case "shell_parse":
		return encode(shlex.Parse(value))
	case "string_width":
		return encode(fuzzy.StringWidth(value))
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
