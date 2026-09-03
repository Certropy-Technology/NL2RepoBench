#!/usr/bin/env bash
set -euo pipefail
mode="${1:?control mode is required}"
case "$mode" in
  stub|forgery|panic|hang|oversized-output|background-process) ;;
  *) printf 'unsupported control mode: %s\n' "$mode" >&2; exit 64 ;;
esac

cat > go.mod <<'MOD'
module github.com/pterm/pterm

go 1.26.5
MOD
: > go.sum
mkdir -p vendor putils
: > vendor/modules.txt
cat > pterm.go <<GO
package pterm

import (
	"errors"
	"fmt"
	"io"
	"os/exec"
	"strings"
	"time"
)

const controlMode = "$mode"
type Color uint8
type Style []Color
type Bars []Bar
type Bar struct { Label string; Value int; Style, LabelStyle *Style }
type RGB struct { R, G, B uint8; Background bool }
type Letter struct { String string; Style *Style; RGB RGB }
type Letters []Letter
type BasicTextPrinter struct { Style *Style; Writer io.Writer }

const (
	Reset Color = iota; Bold; Fuzzy; Italic; Underscore; Blink; FastBlink; Reverse; Concealed; Strikethrough
	FgBlack Color = 30; FgRed Color = 31; FgGreen Color = 32; FgYellow Color = 33
	FgBlue Color = 34; FgMagenta Color = 35; FgCyan Color = 36; FgWhite Color = 37; FgDefault Color = 39
	FgDarkGray Color = 90; FgLightRed Color = 91; FgLightGreen Color = 92; FgLightYellow Color = 93
	FgLightBlue Color = 94; FgLightMagenta Color = 95; FgLightCyan Color = 96; FgLightWhite Color = 97; FgGray = FgDarkGray
	BgBlack Color = 40; BgRed Color = 41; BgGreen Color = 42; BgYellow Color = 43
	BgBlue Color = 44; BgMagenta Color = 45; BgCyan Color = 46; BgWhite Color = 47; BgDefault Color = 49
	BgDarkGray Color = 100; BgLightRed Color = 101; BgLightGreen Color = 102; BgLightYellow Color = 103
	BgLightBlue Color = 104; BgLightMagenta Color = 105; BgLightCyan Color = 106; BgLightWhite Color = 107; BgGray = BgDarkGray
)

var DefaultBasicText BasicTextPrinter
var ErrHexCodeIsInvalid = errors.New("hex code is not valid")

func controlled() string {
	switch controlMode {
	case "forgery":
		return "forged"
	case "panic":
		panic("controlled panic")
	case "hang":
		time.Sleep(60 * time.Second)
	case "oversized-output":
		return strings.Repeat("x", 300000)
	case "background-process":
		_ = exec.Command("sh", "-c", "sleep 60").Start()
		time.Sleep(60 * time.Second)
	}
	return ""
}

func EnableColor() {}
func DisableColor() {}
func Sprint(...any) string { return controlled() }
func Sprintf(string, ...any) string { return controlled() }
func Sprintfln(string, ...any) string { return controlled() }
func Sprintln(...any) string { return controlled() }
func Sprinto(...any) string { return controlled() }
func RemoveColorFromString(...any) string { return controlled() }
func NewStyle(colors ...Color) *Style { value := Style(colors); return &value }
func (c Color) String() string { return controlled() }
func (c Color) Sprint(...any) string { return controlled() }
func (c Color) Sprintln(...any) string { return controlled() }
func (c Color) Sprintf(string, ...any) string { return controlled() }
func (c Color) Sprintfln(string, ...any) string { return controlled() }
func (c Color) ToStyle() *Style { value := Style{c}; return &value }
func (s Style) Add(values ...Style) Style { for _, value := range values { s = append(s, value...) }; return s }
func (s Style) RemoveColor(...Color) Style { return s }
func (s Style) String() string { return controlled() }
func (s Style) Code() string { return controlled() }
func (s Style) Sprint(...any) string { return controlled() }
func (s Style) Sprintln(...any) string { return controlled() }
func (s Style) Sprintf(string, ...any) string { return controlled() }
func (s Style) Sprintfln(string, ...any) string { return controlled() }
func (p BasicTextPrinter) WithStyle(style *Style) *BasicTextPrinter { p.Style = style; return &p }
func (p BasicTextPrinter) WithWriter(writer io.Writer) *BasicTextPrinter { p.Writer = writer; return &p }
func (p BasicTextPrinter) Sprint(...any) string { return controlled() }
func (p BasicTextPrinter) Sprintln(...any) string { return controlled() }
func (p BasicTextPrinter) Sprintf(string, ...any) string { return controlled() }
func (p BasicTextPrinter) Sprintfln(string, ...any) string { return controlled() }
func (p Bar) WithLabel(value string) *Bar { p.Label = value; return &p }
func (p Bar) WithValue(value int) *Bar { p.Value = value; return &p }
func (p Bar) WithStyle(value *Style) *Bar { p.Style = value; return &p }
func (p Bar) WithLabelStyle(value *Style) *Bar { p.LabelStyle = value; return &p }
var _ = fmt.Sprint
GO
cat > putils/putils.go <<'GO'
package putils
import "github.com/pterm/pterm"
func CenterText(string) string { return pterm.Sprint() }
func RGBFromHEX(string) (pterm.RGB, error) { return pterm.RGB{}, nil }
func LettersFromString(string) pterm.Letters { return nil }
func LettersFromStringWithStyle(string, *pterm.Style) pterm.Letters { return nil }
func LettersFromStringWithRGB(string, pterm.RGB) pterm.Letters { return nil }
GO
