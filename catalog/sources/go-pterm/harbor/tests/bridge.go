package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"os"

	"github.com/pterm/pterm"
	"github.com/pterm/pterm/putils"
)

var (
	_ = pterm.Sprint
	_ = pterm.Sprintf
	_ = pterm.Sprintfln
	_ = pterm.Sprintln
	_ = pterm.Sprinto
	_ = pterm.RemoveColorFromString
	_ = pterm.NewStyle
	_ = pterm.Color.Sprintf
	_ = pterm.Color.Sprintfln
	_ = pterm.Style.Sprintf
	_ = pterm.Style.Sprintfln
	_ = pterm.BasicTextPrinter.WithWriter
	_ = pterm.BasicTextPrinter.Sprintf
	_ = pterm.BasicTextPrinter.Sprintfln
	_ = pterm.ErrHexCodeIsInvalid
	_ pterm.Bars
	_ = []pterm.Color{
		pterm.FgBlack, pterm.FgRed, pterm.FgGreen, pterm.FgYellow,
		pterm.FgBlue, pterm.FgMagenta, pterm.FgCyan, pterm.FgWhite,
		pterm.FgDefault, pterm.FgDarkGray, pterm.FgLightRed,
		pterm.FgLightGreen, pterm.FgLightYellow, pterm.FgLightBlue,
		pterm.FgLightMagenta, pterm.FgLightCyan, pterm.FgLightWhite,
		pterm.FgGray, pterm.BgBlack, pterm.BgRed, pterm.BgGreen,
		pterm.BgYellow, pterm.BgBlue, pterm.BgMagenta, pterm.BgCyan,
		pterm.BgWhite, pterm.BgDefault, pterm.BgDarkGray,
		pterm.BgLightRed, pterm.BgLightGreen, pterm.BgLightYellow,
		pterm.BgLightBlue, pterm.BgLightMagenta, pterm.BgLightCyan,
		pterm.BgLightWhite, pterm.BgGray, pterm.Reset, pterm.Bold,
		pterm.Fuzzy, pterm.Italic, pterm.Underscore, pterm.Blink,
		pterm.FastBlink, pterm.Reverse, pterm.Concealed,
		pterm.Strikethrough,
	}
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

type styleView struct {
	Code   string `json:"code"`
	Output string `json:"output,omitempty"`
}

type barView struct {
	Label          string `json:"label"`
	Value          int    `json:"value"`
	StyleCode      string `json:"style_code"`
	LabelStyleCode string `json:"label_style_code"`
}

type letterView struct {
	String     string `json:"string"`
	StyleCode  string `json:"style_code"`
	R          uint8  `json:"r"`
	G          uint8  `json:"g"`
	B          uint8  `json:"b"`
	Background bool   `json:"background"`
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 128*1024)
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

func handle(input request) response {
	switch input.Operation {
	case "format":
		return format(input.Args)
	case "color":
		return color(input.Args)
	case "style":
		return style(input.Args)
	case "basic_text":
		return basicText(input.Args)
	case "strip":
		var text string
		if err := decodeArgs(input.Args, &text); err != nil {
			return invalid(err)
		}
		return response{Value: pterm.RemoveColorFromString(text)}
	case "bar":
		return bar(input.Args)
	case "center_text":
		var text string
		if err := decodeArgs(input.Args, &text); err != nil {
			return invalid(err)
		}
		return response{Value: putils.CenterText(text)}
	case "rgb_from_hex":
		var text string
		if err := decodeArgs(input.Args, &text); err != nil {
			return invalid(err)
		}
		rgb, err := putils.RGBFromHEX(text)
		if err != nil {
			return failed(err)
		}
		return response{Value: rgb}
	case "letters":
		return letters(input.Args)
	default:
		return response{ErrorType: "InvalidInput", Message: "unknown operation"}
	}
}

func format(args []json.RawMessage) response {
	var mode string
	var formatText string
	var values []any
	if len(args) != 3 {
		return invalid(fmt.Errorf("expected mode, format text, and values"))
	}
	if err := json.Unmarshal(args[0], &mode); err != nil {
		return invalid(err)
	}
	if err := json.Unmarshal(args[1], &formatText); err != nil {
		return invalid(err)
	}
	decoded, err := decodeValues(args[2])
	if err != nil {
		return invalid(err)
	}
	values = decoded
	var output string
	switch mode {
	case "sprint":
		output = pterm.Sprint(values...)
	case "sprintln":
		output = pterm.Sprintln(values...)
	case "sprintf":
		output = pterm.Sprintf(formatText, values...)
	case "sprintfln":
		output = pterm.Sprintfln(formatText, values...)
	case "sprinto":
		output = pterm.Sprinto(values...)
	default:
		return invalid(fmt.Errorf("unknown format mode"))
	}
	return response{Value: output}
}

func color(args []json.RawMessage) response {
	var code uint8
	var mode string
	var text string
	var enabled bool
	if err := decodeArgs(args, &code, &mode, &text, &enabled); err != nil {
		return invalid(err)
	}
	setColor(enabled)
	c := pterm.Color(code)
	switch mode {
	case "sprint":
		return response{Value: c.Sprint(text)}
	case "sprintln":
		return response{Value: c.Sprintln(text)}
	case "string":
		return response{Value: c.String()}
	case "to_style":
		return response{Value: c.ToStyle().Code()}
	default:
		return invalid(fmt.Errorf("unknown color mode"))
	}
}

func style(args []json.RawMessage) response {
	var rawCodes []uint8
	var mode string
	var text string
	var enabled bool
	var rawOther []uint8
	if err := decodeArgs(args, &rawCodes, &mode, &text, &enabled, &rawOther); err != nil {
		return invalid(err)
	}
	setColor(enabled)
	base := colors(rawCodes)
	result := base
	switch mode {
	case "sprint":
		return response{Value: styleView{Code: result.Code(), Output: result.Sprint(text)}}
	case "sprintln":
		return response{Value: styleView{Code: result.Code(), Output: result.Sprintln(text)}}
	case "add":
		result = result.Add(colors(rawOther))
	case "remove":
		result = result.RemoveColor(colors(rawOther)...)
	case "code":
		// The unmodified code is returned below.
	default:
		return invalid(fmt.Errorf("unknown style mode"))
	}
	return response{Value: styleView{Code: result.Code()}}
}

func basicText(args []json.RawMessage) response {
	var rawCodes []uint8
	var mode string
	var text string
	var enabled bool
	if err := decodeArgs(args, &rawCodes, &mode, &text, &enabled); err != nil {
		return invalid(err)
	}
	setColor(enabled)
	printer := pterm.DefaultBasicText
	if rawCodes != nil {
		configured := colors(rawCodes)
		printer = *printer.WithStyle(&configured)
	}
	switch mode {
	case "sprint":
		return response{Value: printer.Sprint(text)}
	case "sprintln":
		return response{Value: printer.Sprintln(text)}
	default:
		return invalid(fmt.Errorf("unknown basic text mode"))
	}
}

func bar(args []json.RawMessage) response {
	var label string
	var value int
	var rawStyle []uint8
	var rawLabelStyle []uint8
	if err := decodeArgs(args, &label, &value, &rawStyle, &rawLabelStyle); err != nil {
		return invalid(err)
	}
	styleValue := colors(rawStyle)
	labelStyleValue := colors(rawLabelStyle)
	original := pterm.Bar{}
	modified := original.WithLabel(label).WithValue(value).
		WithStyle(&styleValue).WithLabelStyle(&labelStyleValue)
	return response{Value: map[string]barView{
		"original": viewBar(original),
		"modified": viewBar(*modified),
	}}
}

func letters(args []json.RawMessage) response {
	var mode string
	var text string
	var rawStyle []uint8
	var rgb pterm.RGB
	if err := decodeArgs(args, &mode, &text, &rawStyle, &rgb); err != nil {
		return invalid(err)
	}
	var values pterm.Letters
	switch mode {
	case "default":
		values = putils.LettersFromString(text)
	case "style":
		styleValue := colors(rawStyle)
		values = putils.LettersFromStringWithStyle(text, &styleValue)
	case "rgb":
		values = putils.LettersFromStringWithRGB(text, rgb)
	default:
		return invalid(fmt.Errorf("unknown letters mode"))
	}
	result := make([]letterView, len(values))
	for index, value := range values {
		var code string
		if value.Style != nil {
			code = value.Style.Code()
		}
		result[index] = letterView{
			String: value.String, StyleCode: code,
			R: value.RGB.R, G: value.RGB.G, B: value.RGB.B,
			Background: value.RGB.Background,
		}
	}
	return response{Value: result}
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

func decodeValues(raw json.RawMessage) ([]any, error) {
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.UseNumber()
	var values []any
	if err := decoder.Decode(&values); err != nil {
		return nil, err
	}
	for index, value := range values {
		number, ok := value.(json.Number)
		if !ok {
			continue
		}
		if integer, err := number.Int64(); err == nil {
			values[index] = integer
			continue
		}
		floating, err := number.Float64()
		if err != nil {
			return nil, err
		}
		values[index] = floating
	}
	return values, nil
}

func colors(values []uint8) pterm.Style {
	result := make(pterm.Style, len(values))
	for index, value := range values {
		result[index] = pterm.Color(value)
	}
	return result
}

func setColor(enabled bool) {
	if enabled {
		pterm.EnableColor()
	} else {
		pterm.DisableColor()
	}
}

func viewBar(value pterm.Bar) barView {
	result := barView{Label: value.Label, Value: value.Value}
	if value.Style != nil {
		result.StyleCode = value.Style.Code()
	}
	if value.LabelStyle != nil {
		result.LabelStyleCode = value.LabelStyle.Code()
	}
	return result
}

func invalid(err error) response {
	return response{ErrorType: "InvalidInput", Message: err.Error()}
}

func failed(err error) response {
	return response{ErrorType: "CallFailed", Message: err.Error()}
}

func writeResponse(encoder *json.Encoder, output response) {
	if err := encoder.Encode(output); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
