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

## API Usage Guide

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

## Implementation Notes

Keep the package paths under `internal/` exactly as specified; the bridge is
placed under `cmd/bridge` inside the same module so these imports remain valid.
Do not add hidden fixtures, evaluator-specific constants, or output to stdout
from library code. The evaluator sends newline-delimited JSON requests to a
bridge binary and checks structured responses. The candidate must compile that
bridge with `-mod=vendor` while offline.
