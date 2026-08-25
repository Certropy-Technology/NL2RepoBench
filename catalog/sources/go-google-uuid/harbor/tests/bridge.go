package main

import (
    "bufio"
    "encoding/json"
    "os"
    "github.com/google/uuid"
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

func main() {
    scanner := bufio.NewScanner(os.Stdin)
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
            _ = encoder.Encode(response{ErrorType: "InvalidInput", Message: err.Error()})
            continue
        }
        _ = encoder.Encode(response{Value: parsed.String()})
    }
}
