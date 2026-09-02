package main

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"sort"
	"strings"

	multierror "github.com/hashicorp/go-multierror"
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

type payload struct {
	Messages [][]string `json:"messages,omitempty"`
	Prefix   string     `json:"prefix,omitempty"`
}

type typedError struct{ text string }

func (e *typedError) Error() string { return e.text }

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func encode(value any) response {
	data, err := json.Marshal(value)
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: data}
}

func decode(args []json.RawMessage) (payload, error) {
	if len(args) != 1 {
		return payload{}, errors.New("expected one payload argument")
	}
	var p payload
	if err := json.Unmarshal(args[0], &p); err != nil {
		return payload{}, err
	}
	if len(p.Messages) > 64 {
		return payload{}, errors.New("too many message groups")
	}
	for _, group := range p.Messages {
		if len(group) > 64 {
			return payload{}, errors.New("too many messages")
		}
		for _, message := range group {
			if len(message) > 4096 {
				return payload{}, errors.New("message is too long")
			}
		}
	}
	return p, nil
}

func errorsFor(messages []string) []error {
	result := make([]error, 0, len(messages))
	for _, message := range messages {
		result = append(result, errors.New(message))
	}
	return result
}

func errorTexts(errs []error) []string {
	result := make([]string, 0, len(errs))
	for _, err := range errs {
		if err != nil {
			result = append(result, err.Error())
		}
	}
	return result
}

func aggregate(messages []string) *multierror.Error {
	var result error
	for _, message := range messages {
		result = multierror.Append(result, errors.New(message))
	}
	if result == nil {
		return &multierror.Error{}
	}
	return result.(*multierror.Error)
}

func flattenGroups(groups [][]string) *multierror.Error {
	outer := &multierror.Error{}
	for _, group := range groups {
		inner := aggregate(group)
		outer.Errors = append(outer.Errors, inner)
	}
	return multierror.Flatten(outer).(*multierror.Error)
}

func call(req request) response {
	p, err := decode(req.Args)
	if err != nil {
		return invalid(err.Error())
	}
	switch req.Operation {
	case "aggregate":
		if len(p.Messages) != 1 {
			return invalid("aggregate requires one message group")
		}
		m := aggregate(p.Messages[0])
		return encode(map[string]any{
			"errors": errorTexts(m.Errors), "len": m.Len(), "text": m.Error(),
			"wrapped": errorTexts(m.WrappedErrors()), "or_nil": m.ErrorOrNil() != nil,
		})
	case "format":
		if len(p.Messages) != 1 {
			return invalid("format requires one message group")
		}
		return encode(multierror.ListFormatFunc(errorsFor(p.Messages[0])))
	case "custom_format":
		if len(p.Messages) != 1 {
			return invalid("custom_format requires one message group")
		}
		m := &multierror.Error{Errors: errorsFor(p.Messages[0])}
		m.ErrorFormat = func(es []error) string { return "custom:" + strings.Join(errorTexts(es), "|") }
		return encode(m.Error())
	case "append_nested":
		if len(p.Messages) != 2 {
			return invalid("append_nested requires two groups")
		}
		outer := aggregate(p.Messages[0])
		inner := aggregate(p.Messages[1])
		result := multierror.Append(outer, inner)
		return encode(map[string]any{"errors": errorTexts(result.Errors), "len": result.Len()})
	case "flatten":
		result := flattenGroups(p.Messages)
		return encode(map[string]any{"errors": errorTexts(result.Errors), "text": result.Error()})
	case "prefix":
		if len(p.Messages) != 1 {
			return invalid("prefix requires one message group")
		}
		result := multierror.Prefix(aggregate(p.Messages[0]), p.Prefix)
		m, ok := result.(*multierror.Error)
		if !ok {
			return response{ErrorType: "CallFailed", Message: "prefix changed multierror type"}
		}
		return encode(map[string]any{"errors": errorTexts(m.Errors), "text": m.Error()})
	case "unwrap":
		if len(p.Messages) != 1 {
			return invalid("unwrap requires one message group")
		}
		m := aggregate(p.Messages[0])
		var chain []string
		var current error = m
		for current != nil && len(chain) <= 64 {
			chain = append(chain, current.Error())
			current = errors.Unwrap(current)
		}
		return encode(chain)
	case "is_as":
		if len(p.Messages) != 1 || len(p.Messages[0]) < 2 {
			return invalid("is_as requires at least two messages")
		}
		sentinel := errors.New(p.Messages[0][0])
		typed := &typedError{text: p.Messages[0][1]}
		m := multierror.Append(nil, sentinel, typed)
		var target *typedError
		return encode(map[string]any{"is": errors.Is(m, sentinel), "as": errors.As(m, &target), "as_text": target.Error()})
	case "sort":
		if len(p.Messages) != 1 {
			return invalid("sort requires one message group")
		}
		m := &multierror.Error{Errors: errorsFor(p.Messages[0])}
		sort.Sort(m)
		return encode(errorTexts(m.Errors))
	case "group":
		if len(p.Messages) != 1 {
			return invalid("group requires one message group")
		}
		var group multierror.Group
		for _, message := range p.Messages[0] {
			message := message
			group.Go(func() error {
				if message == "" {
					return nil
				}
				return errors.New(message)
			})
		}
		result := group.Wait()
		if result == nil {
			return encode(map[string]any{"errors": []string{}, "nil": true})
		}
		texts := errorTexts(result.Errors)
		sort.Strings(texts)
		return encode(map[string]any{"errors": texts, "nil": false})
	case "invalid":
		return invalid("known operation received invalid request")
	default:
		return invalid(fmt.Sprintf("unknown operation: %s", req.Operation))
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var req request
		if err := json.Unmarshal(scanner.Bytes(), &req); err != nil {
			_ = encoder.Encode(invalid(err.Error()))
			continue
		}
		if err := encoder.Encode(call(req)); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
