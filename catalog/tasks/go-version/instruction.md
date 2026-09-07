# Build `go-version`

## Project Description

Create a pure-Go module implementing the public version parsing and constraint
behavior of `github.com/hashicorp/go-version`. The module path must be exactly
`github.com/hashicorp/go-version`, and the root package name must be `version`.
The implementation must be deterministic and self-contained.

## Supports

- Linux/amd64 with Go 1.26.5.
- A root `go.mod` with the exact module path, a valid Go version, and a complete
  offline module layout. This task has no third-party runtime dependencies.
- `GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off GOPROXY=off GOSUMDB=off`
  and `GOTOOLCHAIN=local`.
- Pure Go only. Do not use cgo, plugins, `unsafe`, external `replace`
  directives, workspaces, generated source, network access, or external
  services.

## Natural Language Instruction

Create the pure-Go `github.com/hashicorp/go-version` module from an empty
workspace. Implement version parsing, normalization, comparison, constraints,
copy-safe accessors, and collection sorting with the exact public API below.

## Project Directory Structure

```text
workspace/
├── go.mod
├── go.sum
├── vendor/modules.txt
└── version.go
```

Expose package `version` at the documented module path. Preserve text/database
interfaces and panic-on-error helpers, but do not include evaluation-only files.

## Examples

```go
v, err := version.NewVersion("v1.4.2-beta.1")
```

```go
constraints, err := version.NewConstraint(">= 1.0, < 2.0")
ok := constraints.Check(v)
```

## Error Handling and Boundary Conditions

Handle strict versus loose syntax, prefixes, leading zeroes, prerelease and
metadata precedence, overflow, invalid constraint ranges, nil comparisons,
copy-safe segment slices, and empty collections as specified. `Must` helpers may
panic only on their documented error path; ordinary malformed input returns an
error.

## API Usage Guide

Implement package `version` at import path `github.com/hashicorp/go-version`
with these public APIs and signatures:

```go
type Version struct { /* private representation */ }
type Constraint struct { /* private representation */ }
type Constraints []*Constraint
type Collection []*Version
type Option func(*options)

func NewVersion(value string, opts ...Option) (*Version, error)
func NewSemver(value string) (*Version, error)
func WithPrefix(prefix string) Option
func Must(value *Version, err error) *Version

func (v *Version) Compare(other *Version) int
func (v *Version) Equal(other *Version) bool
func (v *Version) GreaterThan(other *Version) bool
func (v *Version) GreaterThanOrEqual(other *Version) bool
func (v *Version) LessThan(other *Version) bool
func (v *Version) LessThanOrEqual(other *Version) bool
func (v *Version) Core() *Version
func (v *Version) Metadata() string
func (v *Version) Prerelease() string
func (v *Version) Original() string
func (v *Version) Prefix() string
func (v *Version) Segments() []int
func (v *Version) Segments64() []int64
func (v *Version) String() string

func NewConstraint(value string) (Constraints, error)
func MustConstraints(value Constraints, err error) Constraints
func (c *Constraint) Check(value *Version) bool
func (c *Constraint) Equals(other *Constraint) bool
func (c *Constraint) Prerelease() bool
func (c *Constraint) String() string
func (c Constraints) Check(value *Version) bool
func (c Constraints) Equals(other Constraints) bool
func (c Constraints) String() string

func (c Collection) Len() int
func (c Collection) Less(i, j int) bool
func (c Collection) Swap(i, j int)
```

`NewVersion` accepts a leading `v`, one or more dot-separated non-negative
integer segments, an optional prerelease suffix, and optional build metadata.
Missing numeric segments are treated as zero for comparison and canonical
formatting. Leading zeroes are normalized in the canonical `String` result.
The original input is returned unchanged by `Original`. `WithPrefix` requires
the supplied prefix to occur at the start of the input, strips it before
parsing, records it in `Prefix`, and keeps the full original text. A missing
prefix is an error. A nil option must be harmless.

`NewSemver` uses the stricter SemVer-shaped parser: it requires the separator
between the core and prerelease forms that the package distinguishes, while it
still accepts the package's documented variable-length numeric core and
normalizes numeric leading zeroes. Invalid syntax returns a non-nil error. Both
parsers reject malformed, overflowing, or otherwise unreasonably long input.
`String` emits normalized numeric segments followed by
`-prerelease` and `+metadata` when present. The zero value of `Version` must
format as `0.0.0`.

Comparison is by numeric segments, using zero-padding when versions have
different specificity, then prerelease precedence. A release is greater than a
prerelease with the same core; numeric prerelease components compare
numerically, numeric components precede non-numeric components, and a shorter
equal prerelease sequence precedes a longer one. Metadata and an explicit
prefix do not affect precedence. The boolean comparison helpers agree with
`Compare`, including safe nil equality behavior for `Equal`.

`Core` returns a new version containing only the first three numeric segments.
`Segments` and `Segments64` return copies, so changing the returned slice must
not mutate the version. `MarshalText`, `UnmarshalText`, `Scan`, and `Value`
should follow the normal text/database contracts exposed by the package.

`NewConstraint` accepts a comma-separated list of comparisons. Supported
operators are an omitted operator or `=`, `!=`, `>`, `>=`, `<`, `<=`, and `~>`.
Whitespace around each comparison is ignored. `Constraints.Check` requires all
constraints to match; prerelease handling follows the package contract: a
constraint without prerelease data does not match a prerelease version, while
a prerelease comparator only matches the same core version. The pessimistic
operator keeps the constrained prefix fixed and permits compatible higher
versions. Invalid constraints return an error. Constraint and collection types
implement their documented sorting/string behavior without mutating caller
owned slices unexpectedly.

Example:

```go
v, err := version.NewVersion("release-v1.4.2-beta.1", version.WithPrefix("release-"))
if err != nil {
    panic(err)
}
limit, _ := version.NewConstraint(">= 1.2, < 2.0")
fmt.Println(v.String(), v.Original(), v.Prefix(), limit.Check(v))
// 1.4.2-beta.1 release-v1.4.2-beta.1 release- false
```

## Implementation Notes

Do not copy the upstream implementation or tests into the submission. Keep
all state instance-local, avoid retaining caller byte/slice storage, and avoid
panics for malformed public inputs except the explicitly panic-on-error
`Must` helpers. The evaluation invokes the API through a bounded newline-
delimited JSON subprocess bridge; the evaluator never imports candidate
code directly. Hidden assertions cover normalization, prefixes, strict and
loose parsing, comparison edge cases, prerelease rules, safe slice copying,
constraint operators, sorting, and malformed bridge requests.
