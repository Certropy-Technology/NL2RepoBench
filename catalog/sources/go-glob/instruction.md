# Build `go-glob`

## Project Description

Create a pure-Go module with module path `github.com/gobwas/glob` and root
package name `glob`. It compiles a compact glob pattern once and matches whole
strings against the compiled pattern. The implementation must be deterministic,
self-contained, and usable through a newline-delimited JSON bridge.

## Natural Language Instruction

Create the `github.com/gobwas/glob` module from an empty `workspace/`. Implement
the compiled root glob API, including syntax diagnostics, whole-string matching,
separator-aware wildcards, character classes, brace alternatives, escaping,
Unicode runes, and metadata access. Keep compilation deterministic and preserve
the distinction between compile-time separator state and the slice exposed by
`Pattern.Separators()`.

The scored project is a library, not a command-line application. The public
`syntax` package and `cmd/globtest` are outside this bounded task even though
the upstream repository contains them. Do not weaken malformed-pattern errors
or replace glob matching with substring matching.

## Supports

- Linux/amd64 with Go 1.26.5 and `CGO_ENABLED=0`.
- One root `go.mod` declaring exactly `github.com/gobwas/glob`, plus `go.sum`
  (it may be empty). Standard-library dependencies only.
- Offline builds with `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
  `GOTOOLCHAIN=local`, and `-mod=vendor`.
- No cgo, plugins, `unsafe`, generated code, workspaces, external `replace`
  directives, network access, or external services.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/
│   └── modules.txt
├── glob.go
├── syntax.go
└── pattern.go
```

The module path in `go.mod` is `github.com/gobwas/glob`, and the root package
is imported as `github.com/gobwas/glob`. The minimum tree above may be split
into additional root `.go` files when each file supports the documented root
API. Do not add a server, generated dependency cache, or runtime download.

## API Usage Guide

All symbols below are in the root package `glob`.

**Import path:** `import glob "github.com/gobwas/glob"`.
In the API pseudocode below, the package identifier is introduced as `import glob`;
the quoted path above is the actual Go source form.

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

## Examples

```go
package main

import "github.com/gobwas/glob"

func main() {
    p := glob.MustCompile("src/**/test?.go", '/')
    _ = p.Match("src/pkg/test1.go")
}
```

```go
p, err := glob.Compile("{cat,dog}.txt")
if err == nil && p.Match("dog.txt") {
    _ = p.String()
}
```

```go
escaped := glob.QuoteMeta("a*b?")
// escaped is `a\\*b\\?` and matches those punctuation characters literally.
```

## Error Handling and Boundary Conditions

- `Compile` returns an error for incomplete escapes, unterminated classes, and
  malformed brace expressions; callers must be able to inspect `*SyntaxError`
  and its byte `Offset` and `Reason`.
- Matching is against the complete string. Empty strings, empty alternatives,
  empty wildcard matches, Unicode input, and a separator rune appearing as a
  literal must follow the API rules above.
- `MustCompile` may panic only for an invalid pattern. Successful compiled
  patterns can be reused concurrently without mutation of their matching
  semantics. All agent, candidate, verifier, Oracle, and control execution is
  NoNetwork.
