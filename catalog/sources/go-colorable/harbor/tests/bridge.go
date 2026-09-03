package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"os"

	colorable "github.com/mattn/go-colorable"
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

func marshal(value any) response {
	data, err := json.Marshal(value)
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: data}
}

func decode(args []json.RawMessage, values ...any) error {
	if len(args) != len(values) {
		return fmt.Errorf("expected %d arguments", len(values))
	}
	for index, value := range values {
		if err := json.Unmarshal(args[index], value); err != nil {
			return fmt.Errorf("argument %d: %w", index, err)
		}
	}
	return nil
}

func errorText(err error) string {
	if err == nil {
		return ""
	}
	return err.Error()
}

func call(input request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = response{ErrorType: "CallFailed", Message: fmt.Sprintf("panic: %v", recovered)}
		}
	}()

	switch input.Operation {
	case "strip":
		var text string
		if err := decode(input.Args, &text); err != nil {
			return invalid(err.Error())
		}
		var output bytes.Buffer
		n, err := colorable.NewNonColorable(&output).Write([]byte(text))
		return marshal(map[string]any{"text": output.String(), "n": n, "error": errorText(err)})
	case "strip_chunks":
		var chunks []string
		if err := decode(input.Args, &chunks); err != nil {
			return invalid(err.Error())
		}
		var output bytes.Buffer
		counts := make([]int, 0, len(chunks))
		writer := colorable.NewNonColorable(&output)
		for _, chunk := range chunks {
			n, err := writer.Write([]byte(chunk))
			if err != nil {
				return marshal(map[string]any{"text": output.String(), "counts": counts, "error": errorText(err)})
			}
			counts = append(counts, n)
		}
		return marshal(map[string]any{"text": output.String(), "counts": counts})
	case "colorable":
		var text string
		if err := decode(input.Args, &text); err != nil {
			return invalid(err.Error())
		}
		reader, writer, err := os.Pipe()
		if err != nil {
			return response{ErrorType: "CallFailed", Message: err.Error()}
		}
		defer reader.Close()
		wrapped := colorable.NewColorable(writer)
		n, writeErr := wrapped.Write([]byte(text))
		closeErr := writer.Close()
		data, readErr := io.ReadAll(reader)
		if writeErr != nil || closeErr != nil || readErr != nil {
			return marshal(map[string]any{"n": n, "text": string(data), "error": errorText(firstError(writeErr, closeErr, readErr))})
		}
		return marshal(map[string]any{"n": n, "text": string(data), "error": ""})
	case "stdio_types":
		_, stdoutOK := colorable.NewColorableStdout().(*os.File)
		_, stderrOK := colorable.NewColorableStderr().(*os.File)
		return marshal(map[string]bool{"stdout_file": stdoutOK, "stderr_file": stderrOK})
	case "enable_colors":
		var enabled bool
		cleanup := colorable.EnableColorsStdout(&enabled)
		beforeCleanup := enabled
		cleanup()
		return marshal(map[string]bool{"enabled": beforeCleanup, "unchanged_after_cleanup": enabled})
	case "nil_colorable":
		panicked := false
		func() {
			defer func() {
				if recover() != nil {
					panicked = true
				}
			}()
			_ = colorable.NewColorable(nil)
		}()
		return marshal(map[string]bool{"panicked": panicked})
	default:
		return invalid("unknown operation")
	}
}

func firstError(errors ...error) error {
	for _, err := range errors {
		if err != nil {
			return err
		}
	}
	return nil
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
