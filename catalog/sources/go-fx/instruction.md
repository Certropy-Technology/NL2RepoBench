# Recreate fx's deterministic utility helpers

## Project Description

Create a Go module at the repository root that reproduces the bounded,
deterministic string helpers used by `github.com/antonmedv/fx`. The evaluator
uses a typed subprocess bridge, so the repository must contain the requested
packages at the exact import paths below. The interactive TUI, terminal input,
clipboard integration, JavaScript runtime, image rendering, and command-line
entrypoint are outside this task.

## Supports

- Linux/amd64 with Go `1.26.5`, `CGO_ENABLED=0`, and `GOWORK=off`.
- One root module whose path is `github.com/antonmedv/fx` and whose `go` directive
  is exactly `1.26.5`.
- Offline builds with `GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off
  GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local`.
- A vendored, offline copy of `github.com/rivo/uniseg v0.4.7`, with matching
  `go.sum` entries and no `replace` directive, workspace file, network fetch,
  cgo, plugin, or external service.

## Natural Language Instruction

Create the frozen utility subset from an empty workspace. Implement the two
library functions at the exact import paths below, preserve shell quoting and
Unicode display-width semantics, and include the bounded JSON-lines bridge.
The bridge is only a transport for these public behaviors; it must not change
their return values or add terminal, filesystem, clock, random, or network
dependencies.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
├── internal/shlex/shlex.go
├── internal/fuzzy/fuzzy.go
└── cmd/bridge/main.go
```

The module path is `github.com/antonmedv/fx`. The bridge imports the internal
packages from within this module, reads one bounded JSON request per line, and
writes one JSON response per line. Diagnostics belong on stderr. Do not add
test, verifier, Oracle, or private-artifact files to the generated workspace.

## API Usage Guide

The exact Go import paths are `github.com/antonmedv/fx/internal/shlex` and
`github.com/antonmedv/fx/internal/fuzzy`:

```go
import "github.com/antonmedv/fx/internal/shlex"
import "github.com/antonmedv/fx/internal/fuzzy"

func main() { /* bridge entrypoint */ }
```

Implement these functions at the exact import paths and signatures:

```go
// github.com/antonmedv/fx/internal/shlex
func Parse(s string) string

// github.com/antonmedv/fx/internal/fuzzy
func StringWidth(s string) int
```

`shlex.Parse` lexes shell-style input and concatenates the values of all word
tokens. Whitespace separates words and is omitted. Double quotes preserve
spaces and allow backslash escaping; single quotes preserve their contents
without escape processing; a backslash outside quotes makes the next rune
literal; and an unquoted `#` starts a comment through the next newline. An
unfinished quoted string is accepted through end of input. If lexing reaches
an invalid internal state, return the empty string as the upstream helper does.

`fuzzy.StringWidth` returns the display width used by fx's fuzzy search for a
UTF-8 string. ASCII characters have their normal terminal width, combining
marks do not add width, and wide East Asian or emoji graphemes follow the
behavior of the pinned `github.com/rivo/uniseg` dependency. Invalid UTF-8 is
handled deterministically and must not panic.

Both functions are pure from the evaluator's perspective: repeated calls
with the same input produce the same output and do not read files, use the
network, or depend on terminal state.

The bridge accepts objects such as these and returns a JSON result object:

```json
{"operation":"parse","value":"echo 'a b' # comment"}
```

```json
{"operation":"string_width","value":"日本語"}
```

Unknown operations, missing values, malformed JSON, and non-string values must
produce a bounded error response rather than panic or arbitrary stdout.

## Examples

```go
shlex.Parse(`echo "two words"`)
// "echotwo words"
```

```go
fuzzy.StringWidth("a\u0301")
// 1
```

## Error Handling and Boundary Conditions

- An unfinished quoted string is accepted through end of input. An unquoted
  `#` starts a comment, but `#` inside single or double quotes is data.
- Backslash escapes the next rune outside quotes and inside double quotes;
  single-quoted contents do not process backslashes.
- Combining marks add no display width, while wide East Asian and emoji
  graphemes follow the pinned `uniseg` package. Invalid UTF-8 is deterministic
  and must never panic.
- Empty input returns an empty parse result and width zero. Long input remains
  bounded by input size and never needs a TTY, service, or network.

## Implementation Notes

Keep the package paths under `internal/` exactly as specified; the bridge is
placed under `cmd/bridge` inside the same module so these imports remain valid.
Do not add hidden fixtures, evaluator-specific constants, or output to stdout
from library code. The evaluator sends newline-delimited JSON requests to a
bridge binary and checks structured responses. The candidate must compile that
bridge with `-mod=vendor` while offline.
