package main

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"math"
	"os"

	"github.com/valyala/fastjson"
)

const (
	maxJSONBytes = 128 * 1024
	maxItems     = 64
	maxDepth     = 32
	maxNodes     = 2048
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

type valueView struct {
	Type      string         `json:"type"`
	Marshaled string         `json:"marshaled"`
	String    *string        `json:"string,omitempty"`
	Bool      *bool          `json:"bool,omitempty"`
	Int64     *int64         `json:"int64,omitempty"`
	Uint64    *uint64        `json:"uint64,omitempty"`
	Float64   *float64       `json:"float64,omitempty"`
	Array     *[]valueView   `json:"array,omitempty"`
	Object    *[]objectEntry `json:"object,omitempty"`
}

type objectEntry struct {
	Key   string    `json:"key"`
	Value valueView `json:"value"`
}

type getView struct {
	Exists bool       `json:"exists"`
	Value  *valueView `json:"value,omitempty"`
}

type handyView struct {
	Exists bool    `json:"exists"`
	String string  `json:"string"`
	Bytes  string  `json:"bytes"`
	Int    int     `json:"int"`
	Float  float64 `json:"float"`
	Bool   bool    `json:"bool"`
}

type mutation struct {
	Operation string `json:"operation"`
	Key       string `json:"key,omitempty"`
	Index     int    `json:"index,omitempty"`
	Value     string `json:"value,omitempty"`
}

type buildNode struct {
	Kind   string       `json:"kind"`
	String string       `json:"string,omitempty"`
	Number string       `json:"number,omitempty"`
	Bool   bool         `json:"bool,omitempty"`
	Array  []buildNode  `json:"array,omitempty"`
	Object []buildEntry `json:"object,omitempty"`
}

type buildEntry struct {
	Key   string    `json:"key"`
	Value buildNode `json:"value"`
}

type budget struct {
	Nodes int
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 256*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			writeResponse(encoder, invalidInput(err))
			continue
		}
		writeResponse(encoder, handle(input))
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func handle(input request) response {
	switch input.Operation {
	case "parse":
		return parseValue(input.Args)
	case "validate":
		return validateJSON(input.Args)
	case "get":
		return getValue(input.Args)
	case "handy":
		return handyLookup(input.Args)
	case "scan":
		return scanValues(input.Args)
	case "mutate":
		return mutateValue(input.Args)
	case "arena_build":
		return arenaBuild(input.Args, false)
	case "arena_reset":
		return arenaBuild(input.Args, true)
	case "pool_parse":
		return poolParse(input.Args)
	default:
		return response{ErrorType: "InvalidInput", Message: "unknown operation"}
	}
}

func parseValue(args []json.RawMessage) response {
	var text string
	if err := decodeArgs(args, &text); err != nil {
		return invalidInput(err)
	}
	if err := boundedJSON(text); err != nil {
		return invalidInput(err)
	}
	value, err := fastjson.Parse(text)
	if err != nil {
		return callFailed(err)
	}
	view, err := snapshot(value, 0, &budget{})
	if err != nil {
		return invalidInput(err)
	}
	return response{Value: view}
}

func validateJSON(args []json.RawMessage) response {
	var text string
	if err := decodeArgs(args, &text); err != nil {
		return invalidInput(err)
	}
	if err := boundedJSON(text); err != nil {
		return invalidInput(err)
	}
	return response{Value: fastjson.Validate(text) == nil}
}

func getValue(args []json.RawMessage) response {
	var text string
	keys := []string{}
	if err := decodeArgs(args, &text, &keys); err != nil {
		return invalidInput(err)
	}
	if err := boundedJSON(text); err != nil {
		return invalidInput(err)
	}
	if err := boundedKeys(keys); err != nil {
		return invalidInput(err)
	}
	var parser fastjson.Parser
	root, err := parser.Parse(text)
	if err != nil {
		return callFailed(err)
	}
	value := root.Get(keys...)
	if value == nil {
		return response{Value: getView{Exists: false}}
	}
	view, err := snapshot(value, 0, &budget{})
	if err != nil {
		return invalidInput(err)
	}
	return response{Value: getView{Exists: true, Value: &view}}
}

func handyLookup(args []json.RawMessage) response {
	var text string
	keys := []string{}
	if err := decodeArgs(args, &text, &keys); err != nil {
		return invalidInput(err)
	}
	if err := boundedJSON(text); err != nil {
		return invalidInput(err)
	}
	if err := boundedKeys(keys); err != nil {
		return invalidInput(err)
	}
	data := []byte(text)
	return response{Value: handyView{
		Exists: fastjson.Exists(data, keys...),
		String: fastjson.GetString(data, keys...),
		Bytes:  string(fastjson.GetBytes(data, keys...)),
		Int:    fastjson.GetInt(data, keys...),
		Float:  fastjson.GetFloat64(data, keys...),
		Bool:   fastjson.GetBool(data, keys...),
	}}
}

func scanValues(args []json.RawMessage) response {
	var text string
	if err := decodeArgs(args, &text); err != nil {
		return invalidInput(err)
	}
	if err := boundedJSON(text); err != nil {
		return invalidInput(err)
	}
	var scanner fastjson.Scanner
	scanner.Init(text)
	views := make([]valueView, 0)
	for scanner.Next() {
		if len(views) >= maxItems {
			return invalidInput(errors.New("stream exceeds 64 values"))
		}
		view, err := snapshot(scanner.Value(), 0, &budget{})
		if err != nil {
			return invalidInput(err)
		}
		views = append(views, view)
	}
	if err := scanner.Error(); err != nil {
		return callFailed(err)
	}
	return response{Value: views}
}

func mutateValue(args []json.RawMessage) response {
	var text string
	mutations := []mutation{}
	if err := decodeArgs(args, &text, &mutations); err != nil {
		return invalidInput(err)
	}
	if err := boundedJSON(text); err != nil {
		return invalidInput(err)
	}
	if len(mutations) > maxItems {
		return invalidInput(errors.New("too many mutations"))
	}
	root, err := fastjson.Parse(text)
	if err != nil {
		return callFailed(err)
	}
	for _, item := range mutations {
		if err := applyMutation(root, item); err != nil {
			return invalidInput(err)
		}
	}
	return response{Value: string(root.MarshalTo(nil))}
}

func applyMutation(root *fastjson.Value, item mutation) error {
	switch item.Operation {
	case "del":
		root.Del(item.Key)
		return nil
	case "set", "set_array_item":
		if err := boundedJSON(item.Value); err != nil {
			return err
		}
		if item.Operation == "set_array_item" && item.Index < 0 {
			return errors.New("array index must be non-negative")
		}
		value, err := fastjson.Parse(item.Value)
		if err != nil {
			return fmt.Errorf("invalid mutation value: %w", err)
		}
		if item.Operation == "set" {
			root.Set(item.Key, value)
		} else {
			root.SetArrayItem(item.Index, value)
		}
		return nil
	default:
		return fmt.Errorf("unknown mutation %q", item.Operation)
	}
}

func arenaBuild(args []json.RawMessage, reset bool) response {
	nodes := []buildNode{}
	if err := decodeArgs(args, &nodes); err != nil {
		return invalidInput(err)
	}
	if len(nodes) != 1 && !reset {
		return invalidInput(errors.New("arena_build expects one node"))
	}
	if len(nodes) != 2 && reset {
		return invalidInput(errors.New("arena_reset expects two nodes"))
	}
	var arena fastjson.Arena
	var output *fastjson.Value
	for index, node := range nodes {
		value, err := buildValue(&arena, node, 0, &budget{})
		if err != nil {
			return invalidInput(err)
		}
		output = value
		if reset && index == 0 {
			arena.Reset()
		}
	}
	return response{Value: string(output.MarshalTo(nil))}
}

func buildValue(
	arena *fastjson.Arena,
	node buildNode,
	depth int,
	limit *budget,
) (*fastjson.Value, error) {
	limit.Nodes++
	if limit.Nodes > maxNodes || depth > maxDepth {
		return nil, errors.New("build exceeds recursive budget")
	}
	switch node.Kind {
	case "null":
		return arena.NewNull(), nil
	case "bool":
		if node.Bool {
			return arena.NewTrue(), nil
		}
		return arena.NewFalse(), nil
	case "string":
		return arena.NewString(node.String), nil
	case "number":
		if len(node.Number) == 0 ||
			(node.Number[0] != '-' && (node.Number[0] < '0' || node.Number[0] > '9')) {
			return nil, errors.New("invalid JSON number")
		}
		var number json.Number
		if err := json.Unmarshal([]byte(node.Number), &number); err != nil {
			return nil, fmt.Errorf("invalid number: %w", err)
		}
		return arena.NewNumberString(node.Number), nil
	case "array":
		value := arena.NewArray()
		for index, child := range node.Array {
			built, err := buildValue(arena, child, depth+1, limit)
			if err != nil {
				return nil, err
			}
			value.SetArrayItem(index, built)
		}
		return value, nil
	case "object":
		value := arena.NewObject()
		for _, entry := range node.Object {
			built, err := buildValue(arena, entry.Value, depth+1, limit)
			if err != nil {
				return nil, err
			}
			value.Set(entry.Key, built)
		}
		return value, nil
	default:
		return nil, fmt.Errorf("unknown build kind %q", node.Kind)
	}
}

func poolParse(args []json.RawMessage) response {
	values := []string{}
	if err := decodeArgs(args, &values); err != nil {
		return invalidInput(err)
	}
	if len(values) > maxItems {
		return invalidInput(errors.New("too many parser-pool values"))
	}
	var pool fastjson.ParserPool
	views := make([]valueView, 0, len(values))
	for _, text := range values {
		if err := boundedJSON(text); err != nil {
			return invalidInput(err)
		}
		parser := pool.Get()
		value, err := parser.Parse(text)
		if err != nil {
			pool.Put(parser)
			return callFailed(err)
		}
		view, err := snapshot(value, 0, &budget{})
		pool.Put(parser)
		if err != nil {
			return invalidInput(err)
		}
		views = append(views, view)
	}
	return response{Value: views}
}

func snapshot(
	value *fastjson.Value,
	depth int,
	limit *budget,
) (valueView, error) {
	limit.Nodes++
	if limit.Nodes > maxNodes || depth > maxDepth {
		return valueView{}, errors.New("value exceeds recursive budget")
	}
	view := valueView{
		Type:      value.Type().String(),
		Marshaled: string(value.MarshalTo(nil)),
	}
	switch value.Type() {
	case fastjson.TypeString:
		data, err := value.StringBytes()
		if err != nil {
			return valueView{}, err
		}
		text := string(data)
		view.String = &text
	case fastjson.TypeNumber:
		if number, err := value.Int64(); err == nil {
			view.Int64 = &number
		}
		if number, err := value.Uint64(); err == nil {
			view.Uint64 = &number
		}
		number, err := value.Float64()
		if err != nil {
			return valueView{}, err
		}
		if !math.IsNaN(number) && !math.IsInf(number, 0) {
			view.Float64 = &number
		}
	case fastjson.TypeTrue, fastjson.TypeFalse:
		boolean, err := value.Bool()
		if err != nil {
			return valueView{}, err
		}
		view.Bool = &boolean
	case fastjson.TypeArray:
		items, err := value.Array()
		if err != nil {
			return valueView{}, err
		}
		children := make([]valueView, 0, len(items))
		for _, item := range items {
			child, err := snapshot(item, depth+1, limit)
			if err != nil {
				return valueView{}, err
			}
			children = append(children, child)
		}
		view.Array = &children
	case fastjson.TypeObject:
		object, err := value.Object()
		if err != nil {
			return valueView{}, err
		}
		entries := make([]objectEntry, 0, object.Len())
		var visitErr error
		object.Visit(func(key []byte, childValue *fastjson.Value) {
			if visitErr != nil {
				return
			}
			child, err := snapshot(childValue, depth+1, limit)
			if err != nil {
				visitErr = err
				return
			}
			entries = append(entries, objectEntry{Key: string(key), Value: child})
		})
		if visitErr != nil {
			return valueView{}, visitErr
		}
		view.Object = &entries
	}
	return view, nil
}

func boundedJSON(value string) error {
	if len(value) > maxJSONBytes {
		return errors.New("JSON input exceeds 128 KiB")
	}
	return nil
}

func boundedKeys(keys []string) error {
	if len(keys) > 16 {
		return errors.New("path exceeds 16 components")
	}
	for _, key := range keys {
		if len(key) > 256 {
			return errors.New("path component exceeds 256 bytes")
		}
	}
	return nil
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

func invalidInput(err error) response {
	return response{ErrorType: "InvalidInput", Message: err.Error()}
}

func callFailed(err error) response {
	return response{ErrorType: "CallFailed", Message: err.Error()}
}

func writeResponse(encoder *json.Encoder, output response) {
	if err := encoder.Encode(output); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
