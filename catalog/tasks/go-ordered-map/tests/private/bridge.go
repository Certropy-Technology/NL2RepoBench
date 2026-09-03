package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strings"

	orderedmap "github.com/iancoleman/orderedmap"
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

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func failed(message string) response {
	return response{ErrorType: "CallFailed", Message: message}
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

func valuesOf(o *orderedmap.OrderedMap) map[string]any {
	values := make(map[string]any, len(o.Values()))
	for key, value := range o.Values() {
		values[key] = summarize(value)
	}
	return values
}

func summarize(value any) any {
	switch value := value.(type) {
	case orderedmap.OrderedMap:
		return map[string]any{"keys": value.Keys(), "values": valuesOf(&value)}
	case *orderedmap.OrderedMap:
		if value == nil {
			return nil
		}
		return map[string]any{"keys": value.Keys(), "values": valuesOf(value)}
	case []any:
		result := make([]any, len(value))
		for index, item := range value {
			result[index] = summarize(item)
		}
		return result
	case map[string]any:
		result := make(map[string]any, len(value))
		for key, item := range value {
			result[key] = summarize(item)
		}
		return result
	default:
		return value
	}
}

func call(input request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = failed(fmt.Sprintf("candidate call panicked: %v", recovered))
		}
	}()

	switch input.Operation {
	case "basic_mutation":
		o := orderedmap.New()
		o.Set("number", 3)
		o.Set("string", "x")
		o.Set("items", []interface{}{"a", float64(2)})
		o.Set("number", 4)
		_, missing := o.Get("missing")
		o.Delete("items")
		o.Delete("absent")
		return response{Value: map[string]any{
			"keys": o.Keys(), "values": valuesOf(o), "missing": missing,
		}}

	case "marshal_default":
		o := orderedmap.New()
		o.Set("number", 4)
		o.Set("special", "\\.<>[]{}_-")
		o.Set("z", 1)
		o.Set("a", 2)
		o.Set("empty_array", []interface{}{})
		o.Set("empty_map", orderedmap.New())
		nested := orderedmap.New()
		nested.Set("e", 1)
		nested.Set("a", 2)
		o.Set("nested", nested)
		compact, err := json.Marshal(o)
		if err != nil {
			return failed(err.Error())
		}
		indented, err := json.MarshalIndent(o, "", "  ")
		if err != nil {
			return failed(err.Error())
		}
		return response{Value: map[string]string{
			"compact": string(compact), "indented": string(indented),
		}}

	case "marshal_no_escape":
		o := orderedmap.New()
		o.SetEscapeHTML(false)
		o.Set("special", "\\.<>[]{}_-")
		input := `{"x":"<>","y":[{"z":["<>"]}]}`
		if err := json.Unmarshal([]byte(input), o); err != nil {
			return failed(err.Error())
		}
		encoded, err := o.MarshalJSON()
		if err != nil {
			return failed(err.Error())
		}
		return response{Value: map[string]string{
			"encoded": strings.ReplaceAll(string(encoded), "\n", ""),
		}}

	case "unmarshal_nested":
		input := `{"root":1,"nested":{"b":"value","a":{"deep":true}},"list":[{"x":2},[{"y":"z"}]]}`
		o := orderedmap.New()
		if err := json.Unmarshal([]byte(input), o); err != nil {
			return failed(err.Error())
		}
		return response{Value: map[string]any{"keys": o.Keys(), "values": valuesOf(o)}}

	case "unmarshal_duplicates":
		input := `{"a": [{}, []], "b": {"x":[1]}, "c":"x", "d":{"x":1}, "b":[{"x":[]}], "c":1, "d":{"y":2}, "e":[{"x":1}], "e":[[]], "e":[{"z":2}], "a":{}, "b":[[1]]}`
		o := orderedmap.New()
		if err := json.Unmarshal([]byte(input), o); err != nil {
			return failed(err.Error())
		}
		return response{Value: map[string]any{"keys": o.Keys(), "values": valuesOf(o)}}

	case "unmarshal_special_keys":
		input := `{ " \u0041\n\r\t\\\\\\\\\\\\\\ "  : { "\\\\" : "value" }, "\\":  "text", "\n": "\r" }`
		o := orderedmap.New()
		if err := json.Unmarshal([]byte(input), o); err != nil {
			return failed(err.Error())
		}
		return response{Value: o.Keys()}

	case "sort_keys":
		o := orderedmap.New()
		o.Set("b", 2)
		o.Set("a", 1)
		o.Set("c", 3)
		o.SortKeys(sort.Strings)
		return response{Value: o.Keys()}

	case "sort_pairs":
		o := orderedmap.New()
		o.Set("low", 1)
		o.Set("high", 3)
		o.Set("middle", 2)
		o.Sort(func(left, right *orderedmap.Pair) bool {
			return left.Value().(int) > right.Value().(int)
		})
		return response{Value: o.Keys()}

	case "pair_access":
		o := orderedmap.New()
		o.Set("first", "value")
		o.Set("second", 2)
		observed := make([]map[string]any, 0, 2)
		o.Sort(func(left, right *orderedmap.Pair) bool {
			observed = append(observed, map[string]any{
				"left_key": left.Key(), "left_value": left.Value(),
				"right_key": right.Key(), "right_value": right.Value(),
			})
			return left.Key() < right.Key()
		})
		return response{Value: map[string]any{"keys": o.Keys(), "observed": observed}}

	case "struct_unmarshal":
		var value struct {
			Data *orderedmap.OrderedMap `json:"data"`
		}
		if err := json.Unmarshal([]byte(`{"data":{"x":1}}`), &value); err != nil {
			return failed(err.Error())
		}
		if value.Data == nil {
			return failed("data was not initialized")
		}
		item, ok := value.Data.Get("x")
		return response{Value: map[string]any{"ok": ok, "value": item, "keys": value.Data.Keys()}}

	case "invalid":
		return invalid("known bridge operation has invalid request")
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
