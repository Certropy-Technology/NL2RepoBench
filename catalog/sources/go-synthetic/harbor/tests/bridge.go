package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "os"
    "example.com/go-synthetic/textx"
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
    encoder := json.NewEncoder(os.Stdout)
    for scanner.Scan() {
        var input request
        if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
            _ = encoder.Encode(response{ErrorType: "InvalidInput", Message: err.Error()})
            continue
        }
        if input.Operation != "normalize" || len(input.Args) != 1 {
            _ = encoder.Encode(response{ErrorType: "InvalidInput", Message: "unknown operation"})
            continue
        }
        var value string
        if err := json.Unmarshal(input.Args[0], &value); err != nil {
            _ = encoder.Encode(response{ErrorType: "InvalidInput", Message: err.Error()})
            continue
        }
        encoded, err := json.Marshal(textx.Normalize(value))
        if err != nil {
            _ = encoder.Encode(response{ErrorType: "CallFailed", Message: err.Error()})
            continue
        }
        _ = encoder.Encode(response{Value: encoded})
    }
    if err := scanner.Err(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}
