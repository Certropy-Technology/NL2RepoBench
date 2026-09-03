# Build `go-glob`

## Project Description

Create a pure-Go module with module path `github.com/gobwas/glob` and root
package name `glob`. It compiles a compact glob pattern once and matches whole
strings against the compiled pattern. The implementation must be deterministic,
self-contained, and usable through a newline-delimited JSON bridge.

## Supports

- Linux/amd64 with Go 1.26.5 and `CGO_ENABLED=0`.
- One root `go.mod` declaring exactly `github.com/gobwas/glob`, plus `go.sum`
  (it may be empty). Standard-library dependencies only.
- Offline builds with `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
  `GOTOOLCHAIN=local`, and `-mod=vendor`.
- No cgo, plugins, `unsafe`, generated code, workspaces, external `replace`
  directives, network access, or external services.

## API Usage Guide

All symbols below are in the root package `glob`.

```go
type SyntaxError struct {
    Offset int
    Reason string
}

type Pattern struct { /* private representation */ }

func Compile(pattern string, separators ...rune) (*Pattern, error)
func MustCompile(pattern string, separators ...rune) *Pattern
func QuoteMeta(s string) string

func (p *Pattern) Match(s string) bool
func (p *Pattern) String() string
func (p *Pattern) Separators() []rune
```

`Compile` parses the complete pattern and returns a `*SyntaxError` for malformed
syntax. `SyntaxError.Offset` is a byte offset in the pattern and `Reason` is a
short diagnostic. `MustCompile` returns the compiled pattern or panics with the
compile error. A compiled pattern is safe to reuse for multiple matches. Its
`String` result is the original pattern text. `Separators` exposes the same
separator slice passed to `Compile`, so later caller mutations are visible
through `Separators`. Matching must still use the separator values captured at
compile time and must not change after such a mutation.

The pattern is matched against the whole input, not a substring. A literal
character matches itself. `*` matches any sequence of non-separator characters,
including the empty sequence. `**` matches any sequence including separators.
`?` matches one non-separator character. When no separators are supplied, `*`
and `**` have the same matching range. Separators affect wildcards only; literal
characters and character classes can match a separator.

Character classes use `[abc]` for a set, `[!abc]` for its negation, `[a-z]` for
a range, and `[!a-z]` for an inverted range. Classes match one rune. Braces
create comma-separated alternatives, for example `{cat,dog}`; nested braces and
empty alternatives are valid. A backslash escapes the next character, so `\*`
matches a literal asterisk and `\\` matches a literal backslash. Commas outside
braces are ordinary literal characters.

`QuoteMeta` returns a new string with every glob metacharacter (`*`, `?`, `\\`,
`[`, `]`, `{`, `}`) escaped. It leaves ordinary characters, including Unicode,
unchanged.

## Implementation Notes

Keep all state instance-local and avoid retaining caller-owned separator storage
for matching. Preserve arbitrary valid UTF-8 strings and treat malformed pattern
syntax as an error rather than panicking. Do not expose hidden tests, expected
values, verifier reports, or source checkouts to the candidate. The evaluator
calls the API through a separate typed subprocess bridge and scores one
verifier-owned fixed leaf covering the public behavior above. Windows-specific
behavior, the debug tree, benchmarks, fuzzing infrastructure, and the example
CLI are outside this Linux contract.
