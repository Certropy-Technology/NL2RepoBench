package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strconv"

	"github.com/jinzhu/copier"
)

const maxRequestBytes = 256 * 1024

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     any    `json:"value,omitempty"`
	ErrorType string `json:"error_type,omitempty"`
	Message   string `json:"message,omitempty"`
}

type person struct {
	Name   string
	Age    int
	Active bool
	Tags   []string
	Meta   map[string]int
}

type renamedInput struct {
	Given string
}

type renamedOutput struct {
	Name string
}

type stringAge struct {
	Age string
}

type taggedInput struct {
	Name    string
	Ignored string
}

type taggedOutput struct {
	Name    string `copier:"Name"`
	Ignored string `copier:"-"`
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), maxRequestBytes)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			writeResponse(encoder, response{ErrorType: "InvalidInput", Message: err.Error()})
			continue
		}
		writeResponse(encoder, handle(input))
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func handle(input request) (out response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			out = response{ErrorType: "CallPanicked", Message: fmt.Sprint(recovered)}
		}
	}()
	switch input.Operation {
	case "basic":
		if len(input.Args) != 0 {
			return invalid("basic takes no arguments")
		}
		from := person{Name: "Ari", Age: 7, Active: true}
		var to person
		if err := copier.Copy(&to, from); err != nil {
			return failed(err)
		}
		return response{Value: to}
	case "slice":
		from := []person{{Name: "Ari", Age: 7}, {Name: "Bo", Age: 9}}
		to := []person{}
		if err := copier.Copy(&to, from); err != nil {
			return failed(err)
		}
		return response{Value: to}
	case "map":
		from := map[string]int{"one": 1, "two": 2}
		to := map[string]int{}
		if err := copier.Copy(&to, from); err != nil {
			return failed(err)
		}
		return response{Value: to}
	case "ignore_empty":
		from := person{}
		to := person{Name: "keep", Age: 9, Active: true}
		if err := copier.CopyWithOption(&to, from, copier.Option{IgnoreEmpty: true}); err != nil {
			return failed(err)
		}
		return response{Value: to}
	case "case_matching":
		type source struct{ name string }
		type exportedSource struct{ Name string }
		type destination struct{ NAME string }
		_ = source{}
		from := exportedSource{Name: "case"}
		var insensitive destination
		var sensitive destination
		if err := copier.Copy(&insensitive, from); err != nil {
			return failed(err)
		}
		if err := copier.CopyWithOption(&sensitive, from, copier.Option{CaseSensitive: true}); err != nil {
			return failed(err)
		}
		return response{Value: map[string]string{"insensitive": insensitive.NAME, "sensitive": sensitive.NAME}}
	case "tags":
		from := taggedInput{Name: "named", Ignored: "source"}
		to := taggedOutput{Ignored: "preserved"}
		if err := copier.Copy(&to, from); err != nil {
			return failed(err)
		}
		return response{Value: to}
	case "field_mapping":
		from := renamedInput{Given: "mapped"}
		var to renamedOutput
		option := copier.Option{FieldNameMapping: []copier.FieldNameMapping{{
			SrcType: renamedInput{},
			DstType: renamedOutput{},
			Mapping: map[string]string{"Given": "Name"},
		}}}
		if err := copier.CopyWithOption(&to, from, option); err != nil {
			return failed(err)
		}
		return response{Value: to}
	case "converter":
		from := stringAge{Age: "42"}
		var to person
		option := copier.Option{Converters: []copier.TypeConverter{{
			SrcType: string(""),
			DstType: int(0),
			Fn: func(value any) (any, error) {
				return strconv.Atoi(value.(string))
			},
		}}}
		if err := copier.CopyWithOption(&to, from, option); err != nil {
			return failed(err)
		}
		return response{Value: to.Age}
	case "deep_copy":
		label := "origin"
		from := person{Tags: []string{"one"}, Meta: map[string]int{"count": 1}}
		from.Name = label
		var to person
		if err := copier.CopyWithOption(&to, from, copier.Option{DeepCopy: true}); err != nil {
			return failed(err)
		}
		from.Tags[0] = "changed"
		from.Meta["count"] = 2
		return response{Value: to}
	case "invalid":
		var to person
		err := copier.Copy(&to, nil)
		if err == nil {
			return response{ErrorType: "UnexpectedSuccess", Message: "nil source copied"}
		}
		return response{Value: "error"}
	default:
		return invalid("unknown operation")
	}
}

func failed(err error) response {
	return response{ErrorType: "CallFailed", Message: err.Error()}
}

func invalid(message string) response {
	return response{ErrorType: "InvalidInput", Message: message}
}

func writeResponse(encoder *json.Encoder, output response) {
	if err := encoder.Encode(output); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
