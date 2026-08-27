package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	humanize "github.com/dustin/go-humanize"
	english "github.com/dustin/go-humanize/english"
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

func decode[T any](args []json.RawMessage, index int, target *T) *response {
	if index >= len(args) {
		return &response{ErrorType: "InvalidInput", Message: "missing argument"}
	}
	if err := json.Unmarshal(args[index], target); err != nil {
		return &response{ErrorType: "InvalidInput", Message: err.Error()}
	}
	return nil
}

func call(req request) response {
	var value any
	switch req.Operation {
	case "bytes":
		var arg uint64
		if err := decode(req.Args, 0, &arg); err != nil || len(req.Args) != 1 {
			if err != nil {
				return *err
			}
			return response{ErrorType: "InvalidInput", Message: "expected one argument"}
		}
		value = humanize.Bytes(arg)
	case "ibytes":
		var arg uint64
		if err := decode(req.Args, 0, &arg); err != nil || len(req.Args) != 1 {
			if err != nil {
				return *err
			}
			return response{ErrorType: "InvalidInput", Message: "expected one argument"}
		}
		value = humanize.IBytes(arg)
	case "comma":
		var arg int64
		if err := decode(req.Args, 0, &arg); err != nil || len(req.Args) != 1 {
			if err != nil {
				return *err
			}
			return response{ErrorType: "InvalidInput", Message: "expected one argument"}
		}
		value = humanize.Comma(arg)
	case "ftoa":
		var arg float64
		if err := decode(req.Args, 0, &arg); err != nil || len(req.Args) != 1 {
			if err != nil {
				return *err
			}
			return response{ErrorType: "InvalidInput", Message: "expected one argument"}
		}
		value = humanize.Ftoa(arg)
	case "ftoa_with_digits":
		var arg float64
		var digits int
		if len(req.Args) != 2 {
			return response{ErrorType: "InvalidInput", Message: "expected two arguments"}
		}
		if err := decode(req.Args, 0, &arg); err != nil {
			return *err
		}
		if err := decode(req.Args, 1, &digits); err != nil {
			return *err
		}
		value = humanize.FtoaWithDigits(arg, digits)
	case "ordinal":
		var arg int
		if err := decode(req.Args, 0, &arg); err != nil || len(req.Args) != 1 {
			if err != nil {
				return *err
			}
			return response{ErrorType: "InvalidInput", Message: "expected one argument"}
		}
		value = humanize.Ordinal(arg)
	case "si":
		var number float64
		var unit string
		if len(req.Args) != 2 {
			return response{ErrorType: "InvalidInput", Message: "expected two arguments"}
		}
		if err := decode(req.Args, 0, &number); err != nil {
			return *err
		}
		if err := decode(req.Args, 1, &unit); err != nil {
			return *err
		}
		value = humanize.SI(number, unit)
	case "si_with_digits":
		var number float64
		var decimals int
		var unit string
		if len(req.Args) != 3 {
			return response{ErrorType: "InvalidInput", Message: "expected three arguments"}
		}
		if err := decode(req.Args, 0, &number); err != nil {
			return *err
		}
		if err := decode(req.Args, 1, &decimals); err != nil {
			return *err
		}
		if err := decode(req.Args, 2, &unit); err != nil {
			return *err
		}
		value = humanize.SIWithDigits(number, decimals, unit)
	case "plural":
		var quantity int
		var singular, plural string
		if len(req.Args) != 3 {
			return response{ErrorType: "InvalidInput", Message: "expected three arguments"}
		}
		if err := decode(req.Args, 0, &quantity); err != nil {
			return *err
		}
		if err := decode(req.Args, 1, &singular); err != nil {
			return *err
		}
		if err := decode(req.Args, 2, &plural); err != nil {
			return *err
		}
		value = english.Plural(quantity, singular, plural)
	case "plural_word":
		var quantity int
		var singular, plural string
		if len(req.Args) != 3 {
			return response{ErrorType: "InvalidInput", Message: "expected three arguments"}
		}
		if err := decode(req.Args, 0, &quantity); err != nil {
			return *err
		}
		if err := decode(req.Args, 1, &singular); err != nil {
			return *err
		}
		if err := decode(req.Args, 2, &plural); err != nil {
			return *err
		}
		value = english.PluralWord(quantity, singular, plural)
	default:
		return response{ErrorType: "InvalidInput", Message: "unknown operation"}
	}
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
		var req request
		if err := json.Unmarshal(scanner.Bytes(), &req); err != nil {
			_ = encoder.Encode(response{ErrorType: "InvalidInput", Message: err.Error()})
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
