# Build the deterministic formatting core of PTerm

## Project Description

Create a pure-Go module implementing a bounded, deterministic slice of
`github.com/pterm/pterm`. PTerm formats terminal text with ANSI colors and
styles and provides small value-oriented helpers. This task covers string
formatting, ANSI color/style rendering, immutable-style builder behavior, and
selected pure helpers from `putils`.

Live printers, progress bars, spinners, interactive input, terminal-size
detection, logging, file downloads, network access, timing, and process control
are outside this task.

## Supports

- Linux/amd64 with Go `1.26.5`.
- One root `go.mod` module with module path `github.com/pterm/pterm`, a
  matching `go.sum`, and no workspace or external `replace` directive.
- Package `pterm` at the module root and package `putils` in `./putils`.
- Pure Go with `CGO_ENABLED=0`; do not use cgo, plugins, generated code,
  network services, or runtime dependency downloads. The repository must build
  with `GOOS=linux GOARCH=amd64 GOWORK=off GOPROXY=off GOSUMDB=off
  GOTOOLCHAIN=local` and `-mod=vendor`.
- The evaluator uses a bounded JSON subprocess bridge. Candidate code is never
  imported into the evaluator process.

## Natural Language Instruction

Create the pure-Go `github.com/pterm/pterm` module from an empty workspace.
Implement only the deterministic string/color/style builders, basic printer,
bar values, and `putils` helpers listed below. Interactive/live components are
outside the task.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
├── pterm.go
├── style.go
├── printer.go
└── putils/
    └── center.go
```

Preserve the root `pterm` and `putils` import paths. Do not add private verifier
or live terminal service code.

## Examples

```go
styled := pterm.Red.Sprint("error")
```

```go
bar := pterm.Bar{Label: "done", Value: 1}
```

## Error Handling and Boundary Conditions

Preserve empty strings, ANSI reset sequences, style composition, Unicode,
width/alignment, builder immutability, and nil/default printer behavior. Fixed
inputs must not depend on terminal state, clock, network, or global mutation.

## API Usage Guide

### Plain string formatting

Package `pterm` must expose:

```go
func Sprint(a ...any) string
func Sprintf(format string, a ...any) string
func Sprintfln(format string, a ...any) string
func Sprintln(a ...any) string
func Sprinto(a ...any) string
func RemoveColorFromString(a ...any) string
```

The first four functions follow the corresponding `fmt.Sprint`, `fmt.Sprintf`,
and `fmt.Sprintln` rules. `Sprintfln` is formatted output followed by exactly
one newline. `Sprinto` prefixes the normal `Sprint` result with carriage return
(`\r`). `RemoveColorFromString` removes ANSI SGR color/style sequences and OSC
8 hyperlink wrappers while preserving their visible text and line breaks.

### ANSI colors and styles

```go
type Color uint8
type Style []Color

func NewStyle(colors ...Color) *Style

func (c Color) String() string
func (c Color) Sprint(a ...any) string
func (c Color) Sprintln(a ...any) string
func (c Color) Sprintf(format string, a ...any) string
func (c Color) Sprintfln(format string, a ...any) string
func (c Color) ToStyle() *Style

func (s Style) Add(styles ...Style) Style
func (s Style) RemoveColor(colors ...Color) Style
func (s Style) String() string
func (s Style) Code() string
func (s Style) Sprint(a ...any) string
func (s Style) Sprintln(a ...any) string
func (s Style) Sprintf(format string, a ...any) string
func (s Style) Sprintfln(format string, a ...any) string
```

Define the standard PTerm color constants with their ANSI SGR values:

- foreground `FgBlack` through `FgWhite` are 30 through 37 and `FgDefault` is
  39;
- bright foreground `FgDarkGray` through `FgLightWhite` are 90 through 97,
  with `FgGray == FgDarkGray`;
- background `BgBlack` through `BgWhite` are 40 through 47 and `BgDefault` is
  49;
- bright background `BgDarkGray` through `BgLightWhite` are 100 through 107,
  with `BgGray == BgDarkGray`;
- options `Reset`, `Bold`, `Fuzzy`, `Italic`, `Underscore`, `Blink`,
  `FastBlink`, `Reverse`, `Concealed`, and `Strikethrough` are 0 through 9.

`Color.String` is the decimal SGR code. `Style.String` and `Style.Code` join
their codes in order with semicolons, returning an empty string for an empty
style. `NewStyle` preserves input order. `Add` appends all supplied styles.
`RemoveColor` removes every occurrence of each requested color while
preserving the order of all remaining entries. These value-receiver operations
must not mutate the style from which they were derived.

When color is enabled, `Sprint` wraps each line independently as
`ESC[<code>m<text>ESC[0m`; an empty string emits no escape sequence. A nested
reset must be followed by the outer color/style code so subsequent text remains
styled. `Sprintln` appends one newline after the rendered text. Formatting
methods expand their format arguments before applying the color or style.
When color is disabled, no new sequence is emitted and any ANSI/OSC styling
already present in the input is stripped.

Expose concurrency-safe global toggles:

```go
func EnableColor()
func DisableColor()
```

The evaluator sets one of these explicitly before every color-sensitive bridge
operation, so package initialization must not affect the result.

### Basic text printer

```go
type BasicTextPrinter struct {
    Style  *Style
    Writer io.Writer
}

var DefaultBasicText BasicTextPrinter

func (p BasicTextPrinter) WithStyle(style *Style) *BasicTextPrinter
func (p BasicTextPrinter) WithWriter(writer io.Writer) *BasicTextPrinter
func (p BasicTextPrinter) Sprint(a ...any) string
func (p BasicTextPrinter) Sprintln(a ...any) string
func (p BasicTextPrinter) Sprintf(format string, a ...any) string
func (p BasicTextPrinter) Sprintfln(format string, a ...any) string
```

The zero/default printer passes text through. A configured style applies the
same rendering rules as `Style`. Builder methods use value receivers, return a
pointer to a modified copy, and never mutate the source printer.

### Bar value and builders

```go
type Bar struct {
    Label      string
    Value      int
    Style      *Style
    LabelStyle *Style
}

type Bars []Bar

func (p Bar) WithLabel(label string) *Bar
func (p Bar) WithValue(value int) *Bar
func (p Bar) WithStyle(style *Style) *Bar
func (p Bar) WithLabelStyle(style *Style) *Bar
```

Chaining builders accumulates all fields on a new value and leaves the
original `Bar` unchanged. Styles are stored by pointer; they are not copied.

### Pure `putils` helpers

Package `putils` at import path `github.com/pterm/pterm/putils` must expose:

```go
func CenterText(text string) string
func RGBFromHEX(hex string) (pterm.RGB, error)
func LettersFromString(text string) pterm.Letters
func LettersFromStringWithStyle(text string, style *pterm.Style) pterm.Letters
func LettersFromStringWithRGB(text string, rgb pterm.RGB) pterm.Letters
```

The required value types are:

```go
type RGB struct {
    R, G, B    uint8
    Background bool
}

type Letter struct {
    String string
    Style  *Style
    RGB    RGB
}

type Letters []Letter
```

`CenterText` centers every line relative to the longest visible line. It adds
equal left/right padding using integer division, so an unmatched spare column
is dropped. ANSI SGR bytes do not count toward visible width. Empty input
returns empty output.

`RGBFromHEX` accepts case-insensitive three- or six-digit hexadecimal colors,
with optional `#` or `0x` text removed before validation. Three digits expand
by doubling each digit. Invalid length returns `ErrHexCodeIsInvalid`; invalid
hex digits return a non-nil parsing error. Successful values have
`Background == false`.

Letter helpers split by Unicode code point, preserve order, and return an empty
slice for empty text. `LettersFromStringWithStyle` stores the exact supplied
style pointer in every letter. `LettersFromStringWithRGB` sets the supplied RGB
value and a non-nil empty style on every letter.

## Implementation Notes

Keep all results deterministic and independent of terminal capability by
honoring explicit color enable/disable calls. Do not retain request buffers or
write diagnostics to stdout. The bridge limits each request to 128 KiB and
rejects unknown operations or malformed argument shapes with structured JSON.
Do not hard-code evaluator examples; implement the public behavior above.
