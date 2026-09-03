package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"math"
	"os"
	"strconv"

	gv "github.com/asaskevich/govalidator/v12"
)

const maxStringBytes = 64 * 1024

type request struct {
	Operation string            `json:"operation"`
	Args      []json.RawMessage `json:"args"`
}

type response struct {
	Value     any    `json:"value,omitempty"`
	ErrorType string `json:"error_type,omitempty"`
	Message   string `json:"message,omitempty"`
}

func invalid(message string) response { return response{ErrorType: "InvalidInput", Message: message} }
func failed(message string) response  { return response{ErrorType: "CallFailed", Message: message} }

func decodeArgs(args []json.RawMessage, values ...any) error {
	if len(args) != len(values) {
		return fmt.Errorf("expected %d arguments", len(values))
	}
	for i, value := range values {
		if err := json.Unmarshal(args[i], value); err != nil {
			return fmt.Errorf("argument %d: %w", i, err)
		}
	}
	return nil
}

func bounded(value string) error {
	if len(value) > maxStringBytes {
		return fmt.Errorf("string exceeds %d bytes", maxStringBytes)
	}
	return nil
}

func validate(name, value string) (bool, error) {
	validators := map[string]gv.Validator{
		"is_email": gv.IsEmail, "is_url": gv.IsURL, "is_request_url": gv.IsRequestURL,
		"is_request_uri": gv.IsRequestURI, "is_alpha": gv.IsAlpha, "is_utf_letter": gv.IsUTFLetter,
		"is_alphanumeric": gv.IsAlphanumeric, "is_utf_letter_numeric": gv.IsUTFLetterNumeric,
		"is_numeric": gv.IsNumeric, "is_utf_numeric": gv.IsUTFNumeric, "is_utf_digit": gv.IsUTFDigit,
		"is_int": gv.IsInt, "is_float": gv.IsFloat, "is_null": gv.IsNull, "is_not_null": gv.IsNotNull,
		"is_ascii": gv.IsASCII, "is_printable_ascii": gv.IsPrintableASCII, "is_base64": gv.IsBase64,
		"is_dns_name": gv.IsDNSName, "is_ip": gv.IsIP, "is_ipv4": gv.IsIPv4, "is_ipv6": gv.IsIPv6,
		"is_port": gv.IsPort, "is_mac": gv.IsMAC, "is_host": gv.IsHost, "is_uuid": gv.IsUUID,
		"is_uuid_v3": gv.IsUUIDv3, "is_uuid_v4": gv.IsUUIDv4, "is_uuid_v5": gv.IsUUIDv5,
		"is_json": gv.IsJSON, "is_hexadecimal": gv.IsHexadecimal, "is_hexcolor": gv.IsHexcolor,
		"is_rgbcolor": gv.IsRGBcolor, "is_latitude": gv.IsLatitude, "is_longitude": gv.IsLongitude,
	}
	fn, ok := validators[name]
	if !ok {
		return false, fmt.Errorf("unknown validator %q", name)
	}
	return fn(value), nil
}

func transform(name, value string, params []string) (any, error) {
	for _, param := range params {
		if err := bounded(param); err != nil {
			return nil, err
		}
	}
	switch name {
	case "contains":
		if len(params) != 1 {
			return nil, fmt.Errorf("contains expects one parameter")
		}
		return gv.Contains(value, params[0]), nil
	case "matches":
		if len(params) != 1 {
			return nil, fmt.Errorf("matches expects one parameter")
		}
		return gv.Matches(value, params[0]), nil
	case "trim":
		if len(params) != 1 {
			return nil, fmt.Errorf("trim expects one parameter")
		}
		return gv.Trim(value, params[0]), nil
	case "left_trim":
		if len(params) != 1 {
			return nil, fmt.Errorf("left_trim expects one parameter")
		}
		return gv.LeftTrim(value, params[0]), nil
	case "right_trim":
		if len(params) != 1 {
			return nil, fmt.Errorf("right_trim expects one parameter")
		}
		return gv.RightTrim(value, params[0]), nil
	case "blacklist":
		if len(params) != 1 {
			return nil, fmt.Errorf("blacklist expects one parameter")
		}
		return gv.BlackList(value, params[0]), nil
	case "whitelist":
		if len(params) != 1 {
			return nil, fmt.Errorf("whitelist expects one parameter")
		}
		return gv.WhiteList(value, params[0]), nil
	case "strip_low":
		if len(params) != 1 {
			return nil, fmt.Errorf("strip_low expects one boolean parameter")
		}
		keep, err := strconv.ParseBool(params[0])
		if err != nil {
			return nil, err
		}
		return gv.StripLow(value, keep), nil
	case "replace_pattern":
		if len(params) != 2 {
			return nil, fmt.Errorf("replace_pattern expects pattern and replacement")
		}
		return gv.ReplacePattern(value, params[0], params[1]), nil
	case "camel_case_to_underscore":
		if len(params) != 0 {
			return nil, fmt.Errorf("camel_case_to_underscore expects no parameters")
		}
		return gv.CamelCaseToUnderscore(value), nil
	case "underscore_to_camel_case":
		if len(params) != 0 {
			return nil, fmt.Errorf("underscore_to_camel_case expects no parameters")
		}
		return gv.UnderscoreToCamelCase(value), nil
	case "reverse":
		if len(params) != 0 {
			return nil, fmt.Errorf("reverse expects no parameters")
		}
		return gv.Reverse(value), nil
	case "safe_file_name":
		if len(params) != 0 {
			return nil, fmt.Errorf("safe_file_name expects no parameters")
		}
		return gv.SafeFileName(value), nil
	case "normalize_email":
		if len(params) != 0 {
			return nil, fmt.Errorf("normalize_email expects no parameters")
		}
		return gv.NormalizeEmail(value)
	case "get_lines":
		if len(params) != 0 {
			return nil, fmt.Errorf("get_lines expects no parameters")
		}
		return gv.GetLines(value), nil
	case "get_line":
		if len(params) != 1 {
			return nil, fmt.Errorf("get_line expects one index")
		}
		index, err := strconv.ParseInt(params[0], 10, 64)
		if err != nil || index < 0 || index > math.MaxInt {
			return nil, fmt.Errorf("invalid line index")
		}
		return gv.GetLine(value, int(index))
	default:
		return nil, fmt.Errorf("unknown transform %q", name)
	}
}

func handle(input request) (result response) {
	defer func() {
		if recovered := recover(); recovered != nil {
			result = failed(fmt.Sprintf("panic: %v", recovered))
		}
	}()
	switch input.Operation {
	case "validate":
		var name, value string
		if err := decodeArgs(input.Args, &name, &value); err != nil {
			return invalid(err.Error())
		}
		if err := bounded(name); err != nil {
			return invalid(err.Error())
		}
		if err := bounded(value); err != nil {
			return invalid(err.Error())
		}
		output, err := validate(name, value)
		if err != nil {
			return invalid(err.Error())
		}
		return response{Value: output}
	case "transform":
		if len(input.Args) < 2 {
			return invalid("transform expects a name and value")
		}
		var name, value string
		if err := decodeArgs(input.Args[:2], &name, &value); err != nil {
			return invalid(err.Error())
		}
		if err := bounded(name); err != nil {
			return invalid(err.Error())
		}
		if err := bounded(value); err != nil {
			return invalid(err.Error())
		}
		params := make([]string, len(input.Args)-2)
		for i := range params {
			if name == "strip_low" {
				var keep bool
				if err := json.Unmarshal(input.Args[i+2], &keep); err != nil {
					return invalid(fmt.Sprintf("argument %d: %v", i+2, err))
				}
				params[i] = strconv.FormatBool(keep)
				continue
			}
			if err := json.Unmarshal(input.Args[i+2], &params[i]); err != nil {
				return invalid(fmt.Sprintf("argument %d: %v", i+2, err))
			}
		}
		output, err := transform(name, value, params)
		if err != nil {
			return failed(err.Error())
		}
		return response{Value: output}
	case "convert":
		if len(input.Args) != 2 {
			return invalid("convert expects a name and JSON value")
		}
		var name string
		if err := json.Unmarshal(input.Args[0], &name); err != nil {
			return invalid(err.Error())
		}
		if err := bounded(name); err != nil {
			return invalid(err.Error())
		}
		var value any
		if err := json.Unmarshal(input.Args[1], &value); err != nil {
			return invalid(err.Error())
		}
		switch name {
		case "to_string":
			return response{Value: gv.ToString(value)}
		case "to_json":
			output, err := gv.ToJSON(value)
			if err != nil {
				return failed(err.Error())
			}
			return response{Value: output}
		case "to_float":
			output, err := gv.ToFloat(value)
			if err != nil {
				return failed(err.Error())
			}
			return response{Value: output}
		case "to_int":
			output, err := gv.ToInt(value)
			if err != nil {
				return failed(err.Error())
			}
			return response{Value: output}
		case "to_boolean":
			var text string
			if err := json.Unmarshal(input.Args[1], &text); err != nil {
				return invalid(err.Error())
			}
			output, err := gv.ToBoolean(text)
			if err != nil {
				return failed(err.Error())
			}
			return response{Value: output}
		default:
			return invalid(fmt.Sprintf("unknown converter %q", name))
		}
	default:
		return invalid("unknown operation")
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 128*1024)
	encoder := json.NewEncoder(os.Stdout)
	for scanner.Scan() {
		var input request
		if err := json.Unmarshal(scanner.Bytes(), &input); err != nil {
			_ = encoder.Encode(invalid(err.Error()))
			continue
		}
		if err := encoder.Encode(handle(input)); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
