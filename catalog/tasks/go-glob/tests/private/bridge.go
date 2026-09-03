package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	glob "github.com/gobwas/glob"
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

func valueOf(value any) response {
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

func compile(pattern, separator string) (*glob.Pattern, error) {
	return glob.Compile(pattern, []rune(separator)...)
}

func mustCompile(pattern, separator string) *glob.Pattern {
	return glob.MustCompile(pattern, []rune(separator)...)
}

func call(input request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = response{ErrorType: "CallFailed", Message: fmt.Sprintf("panic: %v", recovered)}
		}
	}()

	switch input.Operation {
	case "match":
		var pattern, separator, subject string
		if err := decode(input.Args, &pattern, &separator, &subject); err != nil {
			return invalid(err.Error())
		}
		compiled, err := compile(pattern, separator)
		if err != nil {
			return valueOf(map[string]any{"ok": false, "error": err.Error()})
		}
		return valueOf(map[string]any{"ok": true, "matched": compiled.Match(subject)})
	case "match_info":
		var pattern, separator, subject string
		if err := decode(input.Args, &pattern, &separator, &subject); err != nil {
			return invalid(err.Error())
		}
		compiled, err := compile(pattern, separator)
		if err != nil {
			return valueOf(map[string]any{"ok": false, "error": err.Error()})
		}
		return valueOf(map[string]any{
			"ok":         true,
			"matched":    compiled.Match(subject),
			"pattern":    compiled.String(),
			"separators": string(compiled.Separators()),
		})
	case "must_match":
		var pattern, separator, subject string
		if err := decode(input.Args, &pattern, &separator, &subject); err != nil {
			return invalid(err.Error())
		}
		compiled := mustCompile(pattern, separator)
		return valueOf(map[string]any{"matched": compiled.Match(subject)})
	case "separator_ownership":
		var pattern, separator, subject string
		if err := decode(input.Args, &pattern, &separator, &subject); err != nil {
			return invalid(err.Error())
		}
		separators := []rune(separator)
		compiled, err := glob.Compile(pattern, separators...)
		if err != nil {
			return valueOf(map[string]any{"ok": false, "error": err.Error()})
		}
		if len(separators) > 0 {
			separators[0] = '#'
		}
		return valueOf(map[string]any{
			"ok":         true,
			"matched":    compiled.Match(subject),
			"separators": string(compiled.Separators()),
		})
	case "quote":
		var text string
		if err := decode(input.Args, &text); err != nil {
			return invalid(err.Error())
		}
		return valueOf(glob.QuoteMeta(text))
	case "compile_error":
		var pattern string
		if err := decode(input.Args, &pattern); err != nil {
			return invalid(err.Error())
		}
		_, err := glob.Compile(pattern)
		if err == nil {
			return valueOf(map[string]any{"ok": true})
		}
		result := map[string]any{"ok": false, "error": err.Error()}
		if syntax, ok := err.(*glob.SyntaxError); ok {
			result["offset"] = syntax.Offset
			result["reason"] = syntax.Reason
		}
		return valueOf(result)
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
