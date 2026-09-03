package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"os"

	"dario.cat/mergo"
)

const maxRequestBytes = 64 * 1024

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     json.RawMessage `json:"value,omitempty"`
	ErrorType string          `json:"error_type,omitempty"`
	Message   string          `json:"message,omitempty"`
}

type child struct {
	Label string `json:"label"`
	Value int    `json:"value"`
}

type record struct {
	Name    string                 `json:"name"`
	Count   int                    `json:"count"`
	Enabled bool                   `json:"enabled"`
	Tags    []int                  `json:"tags"`
	Meta    map[string]interface{} `json:"meta"`
	Child   *child                 `json:"child"`
	hidden  string
}

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func callFailed(err error) response {
	return response{ErrorType: "CallFailed", Message: err.Error()}
}

func encode(value interface{}) response {
	payload, err := json.Marshal(value)
	if err != nil {
		return callFailed(err)
	}
	return response{Value: payload}
}

func decode(args []json.RawMessage, index int, target interface{}) error {
	if index >= len(args) {
		return fmt.Errorf("missing argument %d", index)
	}
	return json.Unmarshal(args[index], target)
}

func decodeJSONMap(raw json.RawMessage) (map[string]interface{}, error) {
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.UseNumber()
	var value map[string]interface{}
	if err := decoder.Decode(&value); err != nil {
		return nil, err
	}
	if value == nil {
		return map[string]interface{}{}, nil
	}
	return normalizeNumbers(value).(map[string]interface{}), nil
}

func normalizeNumbers(value interface{}) interface{} {
	switch item := value.(type) {
	case json.Number:
		if integer, err := item.Int64(); err == nil {
			return int(integer)
		}
		if number, err := item.Float64(); err == nil {
			return number
		}
		return item.String()
	case map[string]interface{}:
		for key, childValue := range item {
			item[key] = normalizeNumbers(childValue)
		}
	case []interface{}:
		for index, childValue := range item {
			item[index] = normalizeNumbers(childValue)
		}
	}
	return value
}

func options(names []string) ([]func(*mergo.Config), error) {
	known := map[string]func(*mergo.Config){
		"override":             mergo.WithOverride,
		"overwrite_empty":      mergo.WithOverwriteWithEmptyValue,
		"override_empty_slice": mergo.WithOverrideEmptySlice,
		"without_dereference":  mergo.WithoutDereference,
		"append_slice":         mergo.WithAppendSlice,
		"type_check":           mergo.WithTypeCheck,
		"slice_deep_copy":      mergo.WithSliceDeepCopy,
	}
	result := make([]func(*mergo.Config), 0, len(names))
	for _, name := range names {
		option, ok := known[name]
		if !ok {
			return nil, fmt.Errorf("unknown option %q", name)
		}
		result = append(result, option)
	}
	return result, nil
}

func recordView(value record) map[string]interface{} {
	return map[string]interface{}{
		"name": value.Name, "count": value.Count, "enabled": value.Enabled,
		"tags": value.Tags, "meta": value.Meta, "child": value.Child,
		"hidden": value.hidden,
	}
}

func mergeRecord(args []json.RawMessage) response {
	if len(args) != 3 {
		return invalid("merge_record expects destination, source, and options")
	}
	var dst, src record
	var names []string
	if err := decode(args, 0, &dst); err != nil {
		return invalid(err.Error())
	}
	if err := decode(args, 1, &src); err != nil {
		return invalid(err.Error())
	}
	if err := decode(args, 2, &names); err != nil {
		return invalid(err.Error())
	}
	dst.hidden = "destination-private"
	src.hidden = "source-private"
	opts, err := options(names)
	if err != nil {
		return invalid(err.Error())
	}
	if err := mergo.Merge(&dst, src, opts...); err != nil {
		return callFailed(err)
	}
	return encode(recordView(dst))
}

func mergeMap(args []json.RawMessage) response {
	if len(args) != 3 {
		return invalid("merge_map expects destination, source, and options")
	}
	var dst, src map[string]interface{}
	var names []string
	if err := decode(args, 0, &dst); err != nil {
		return invalid(err.Error())
	}
	if err := decode(args, 1, &src); err != nil {
		return invalid(err.Error())
	}
	if err := decode(args, 2, &names); err != nil {
		return invalid(err.Error())
	}
	opts, err := options(names)
	if err != nil {
		return invalid(err.Error())
	}
	if err := mergo.Merge(&dst, src, opts...); err != nil {
		return callFailed(err)
	}
	return encode(dst)
}

func mapToRecord(args []json.RawMessage) response {
	if len(args) != 3 {
		return invalid("map_to_record expects destination, source, and options")
	}
	var dst record
	var names []string
	if err := decode(args, 0, &dst); err != nil {
		return invalid(err.Error())
	}
	var sourceRaw json.RawMessage
	if err := decode(args, 1, &sourceRaw); err != nil {
		return invalid(err.Error())
	}
	src, err := decodeJSONMap(sourceRaw)
	if err != nil {
		return invalid(err.Error())
	}
	if err := decode(args, 2, &names); err != nil {
		return invalid(err.Error())
	}
	dst.hidden = "destination-private"
	opts, err := options(names)
	if err != nil {
		return invalid(err.Error())
	}
	if err := mergo.Map(&dst, src, opts...); err != nil {
		return callFailed(err)
	}
	return encode(recordView(dst))
}

func recordToMap(args []json.RawMessage) response {
	if len(args) != 3 {
		return invalid("record_to_map expects destination, source, and options")
	}
	var dst map[string]interface{}
	var src record
	var names []string
	if err := decode(args, 0, &dst); err != nil {
		return invalid(err.Error())
	}
	if err := decode(args, 1, &src); err != nil {
		return invalid(err.Error())
	}
	if err := decode(args, 2, &names); err != nil {
		return invalid(err.Error())
	}
	src.hidden = "source-private"
	opts, err := options(names)
	if err != nil {
		return invalid(err.Error())
	}
	if err := mergo.Map(&dst, src, opts...); err != nil {
		return callFailed(err)
	}
	return encode(dst)
}

func errorCall(args []json.RawMessage) response {
	if len(args) != 1 {
		return invalid("error expects a case name")
	}
	var name string
	if err := decode(args, 0, &name); err != nil {
		return invalid(err.Error())
	}
	var err error
	switch name {
	case "nil":
		err = mergo.Merge(nil, nil)
	case "non_pointer":
		err = mergo.Merge(record{}, record{})
	case "different_types":
		err = mergo.Merge(&record{}, map[string]interface{}{})
	case "unsupported":
		value := 0
		err = mergo.Merge(&value, 1)
	case "expected_map":
		err = mergo.Map(&[]int{}, record{})
	case "expected_struct":
		err = mergo.Map(&[]int{}, map[string]interface{}{})
	default:
		return invalid("unknown error case")
	}
	if err == nil {
		return callFailed(fmt.Errorf("expected an error"))
	}
	return encode(err.Error())
}

func dispatch(item request) response {
	switch item.Operation {
	case "merge_record":
		return mergeRecord(item.Args)
	case "merge_map":
		return mergeMap(item.Args)
	case "map_to_record":
		return mapToRecord(item.Args)
	case "record_to_map":
		return recordToMap(item.Args)
	case "error":
		return errorCall(item.Args)
	default:
		return invalid("unknown operation")
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), maxRequestBytes)
	writer := bufio.NewWriter(os.Stdout)
	defer writer.Flush()
	for scanner.Scan() {
		var item request
		var result response
		if err := json.Unmarshal(scanner.Bytes(), &item); err != nil {
			result = invalid(err.Error())
		} else {
			result = dispatch(item)
		}
		payload, _ := json.Marshal(result)
		fmt.Fprintln(writer, string(payload))
	}
	if err := scanner.Err(); err != nil {
		payload, _ := json.Marshal(invalid("request exceeds limit"))
		fmt.Fprintln(writer, string(payload))
	}
}
