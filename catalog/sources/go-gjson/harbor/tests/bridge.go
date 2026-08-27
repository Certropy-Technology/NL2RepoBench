package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	"github.com/tidwall/gjson"
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

type resultView struct {
	Type     string  `json:"type"`
	Raw      string  `json:"raw"`
	Str      string  `json:"str"`
	Num      float64 `json:"num"`
	Index    int     `json:"index"`
	Exists   bool    `json:"exists"`
	Bool     bool    `json:"bool"`
	Int      int64   `json:"int"`
	Uint     uint64  `json:"uint"`
	Float    float64 `json:"float"`
	String   string  `json:"string"`
	IsObject bool    `json:"is_object"`
	IsArray  bool    `json:"is_array"`
	IsBool   bool    `json:"is_bool"`
}

func view(result gjson.Result) resultView {
	return resultView{
		Type: result.Type.String(), Raw: result.Raw, Str: result.Str,
		Num: result.Num, Index: result.Index, Exists: result.Exists(),
		Bool: result.Bool(), Int: result.Int(), Uint: result.Uint(),
		Float: result.Float(), String: result.String(),
		IsObject: result.IsObject(), IsArray: result.IsArray(), IsBool: result.IsBool(),
	}
}

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func boundedPath(path string) *response {
	if len(path) > 256 {
		r := invalid("path exceeds 256 bytes")
		return &r
	}
	components := 1
	for i := 0; i < len(path); i++ {
		if path[i] == '.' && (i == 0 || path[i-1] != '\\') {
			components++
		}
	}
	if components > 16 {
		r := invalid("path exceeds 16 components")
		return &r
	}
	return nil
}

func decodeString(args []json.RawMessage, index int) (string, *response) {
	if index >= len(args) {
		r := invalid("missing argument")
		return "", &r
	}
	var value string
	if err := json.Unmarshal(args[index], &value); err != nil {
		r := invalid(err.Error())
		return "", &r
	}
	return value, nil
}

func call(input request) response {
	if len(input.Args) == 0 {
		return invalid("missing arguments")
	}
	switch input.Operation {
	case "get":
		jsonText, errResponse := decodeString(input.Args, 0)
		if errResponse != nil {
			return *errResponse
		}
		path, errResponse := decodeString(input.Args, 1)
		if errResponse != nil {
			return *errResponse
		}
		if errResponse := boundedPath(path); errResponse != nil {
			return *errResponse
		}
		return encodeValue(view(gjson.Get(jsonText, path)))
	case "parse":
		jsonText, errResponse := decodeString(input.Args, 0)
		if errResponse != nil {
			return *errResponse
		}
		return encodeValue(view(gjson.Parse(jsonText)))
	case "valid":
		jsonText, errResponse := decodeString(input.Args, 0)
		if errResponse != nil {
			return *errResponse
		}
		return encodeValue(gjson.Valid(jsonText))
	case "escape":
		component, errResponse := decodeString(input.Args, 0)
		if errResponse != nil {
			return *errResponse
		}
		return encodeValue(gjson.Escape(component))
	case "get_many":
		jsonText, errResponse := decodeString(input.Args, 0)
		if errResponse != nil {
			return *errResponse
		}
		if len(input.Args) != 2 {
			return invalid("get_many expects JSON and a path array")
		}
		var paths []string
		if err := json.Unmarshal(input.Args[1], &paths); err != nil {
			return invalid(err.Error())
		}
		if len(paths) > 32 {
			return invalid("too many paths")
		}
		for _, path := range paths {
			if errResponse := boundedPath(path); errResponse != nil {
				return *errResponse
			}
		}
		results := gjson.GetMany(jsonText, paths...)
		views := make([]resultView, len(results))
		for i, result := range results {
			views[i] = view(result)
		}
		return encodeValue(views)
	default:
		return invalid("unknown operation")
	}
}

func encodeValue(value any) response {
	encoded, err := json.Marshal(value)
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: encoded}
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
