package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"

	"github.com/TheAlgorithms/Go/conversion"
)

const maxRequestBytes = 64 * 1024

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     any    `json:"value,omitempty"`
	ErrorType string `json:"error_type,omitempty"`
	Message   string `json:"message,omitempty"`
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), maxRequestBytes)
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
	case "base64_encode":
		var value string
		if err := decodeArgs(input.Args, &value); err != nil {
			return invalidInput(err)
		}
		return response{Value: conversion.Base64Encode([]byte(value))}
	case "base64_decode":
		var value string
		if err := decodeArgs(input.Args, &value); err != nil {
			return invalidInput(err)
		}
		return response{Value: string(conversion.Base64Decode(value))}
	case "binary_to_decimal":
		var value string
		if err := decodeArgs(input.Args, &value); err != nil {
			return invalidInput(err)
		}
		converted, err := conversion.BinaryToDecimal(value)
		return callResult(converted, err)
	case "reverse":
		var value string
		if err := decodeArgs(input.Args, &value); err != nil {
			return invalidInput(err)
		}
		return response{Value: conversion.Reverse(value)}
	case "decimal_to_binary":
		var value int
		if err := decodeArgs(input.Args, &value); err != nil {
			return invalidInput(err)
		}
		converted, err := conversion.DecimalToBinary(value)
		return callResult(converted, err)
	case "int_to_roman":
		var value int
		if err := decodeArgs(input.Args, &value); err != nil {
			return invalidInput(err)
		}
		converted, err := conversion.IntToRoman(value)
		return callResult(converted, err)
	case "roman_to_int":
		var value string
		if err := decodeArgs(input.Args, &value); err != nil {
			return invalidInput(err)
		}
		converted, err := conversion.RomanToInt(value)
		return callResult(converted, err)
	case "hex_to_rgb":
		var value uint
		if err := decodeArgs(input.Args, &value); err != nil {
			return invalidInput(err)
		}
		red, green, blue := conversion.HEXToRGB(value)
		return response{Value: [3]byte{red, green, blue}}
	case "rgb_to_hex":
		var red byte
		var green byte
		var blue byte
		if err := decodeArgs(input.Args, &red, &green, &blue); err != nil {
			return invalidInput(err)
		}
		return response{Value: conversion.RGBToHEX(red, green, blue)}
	default:
		return response{ErrorType: "InvalidInput", Message: "unknown operation"}
	}
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

func callResult(value any, err error) response {
	if err != nil {
		return response{ErrorType: "CallFailed", Message: err.Error()}
	}
	return response{Value: value}
}

func invalidInput(err error) response {
	return response{ErrorType: "InvalidInput", Message: err.Error()}
}

func writeResponse(encoder *json.Encoder, output response) {
	if err := encoder.Encode(output); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
