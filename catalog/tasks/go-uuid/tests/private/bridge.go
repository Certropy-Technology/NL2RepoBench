package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	"github.com/google/uuid"
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

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			_ = encoder.Encode(response{ErrorType: "InvalidInput", Message: err.Error()})
			continue
		}
		if input.Operation != "parse" || len(input.Args) != 1 {
			_ = encoder.Encode(response{ErrorType: "InvalidInput", Message: "unknown operation"})
			continue
		}
		var text string
		if err := json.Unmarshal(input.Args[0], &text); err != nil {
			_ = encoder.Encode(response{ErrorType: "InvalidInput", Message: err.Error()})
			continue
		}
		parsed, err := uuid.Parse(text)
		if err != nil {
			_ = encoder.Encode(response{ErrorType: "CallFailed", Message: err.Error()})
			continue
		}
		value, err := json.Marshal(parsed.String())
		if err != nil {
			_ = encoder.Encode(response{ErrorType: "CallFailed", Message: err.Error()})
			continue
		}
		if err := encoder.Encode(response{Value: value}); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
