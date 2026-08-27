# Build a semantic version and constraint library

## Project Description

Create a pure-Go semantic version library compatible with Semantic Versioning
2.0.0. The repository must be a single Go module whose module path is
`github.com/Masterminds/semver/v3`. The task covers parsing, formatting,
comparison, safe increments, validated prerelease and metadata updates,
constraint checks, and version collection sorting.

## Supports

- Linux/amd64 with Go 1.26.5.
- A root `go.mod` declaring the exact module path and Go version, a `go.sum`,
  and a complete `vendor/modules.txt` closure. This package has no third-party
  runtime dependencies.
- Builds with `GOOS=linux`, `GOARCH=amd64`, `CGO_ENABLED=0`, `GOWORK=off`,
  `GOPROXY=off`, `GOSUMDB=off`, and `GOTOOLCHAIN=local`.
- One pure-Go module only. Do not use cgo, plugins, `unsafe`, `go generate`, a
  workspace, an external `replace` directive, network access, or external
  services.

## API Usage Guide

Implement package `semver` at import path
`github.com/Masterminds/semver/v3` with these public APIs:

```go
type Version struct { /* private representation */ }

func NewVersion(value string) (*Version, error)
func StrictNewVersion(value string) (*Version, error)

func (v Version) Major() uint64
func (v Version) Minor() uint64
func (v Version) Patch() uint64
func (v Version) Prerelease() string
func (v Version) Metadata() string
func (v Version) String() string
func (v *Version) Original() string

func (v *Version) Compare(other *Version) int
func (v Version) IncMajorE() (Version, error)
func (v Version) IncMinorE() (Version, error)
func (v Version) IncPatchE() (Version, error)
func (v Version) SetPrerelease(value string) (Version, error)
func (v Version) SetMetadata(value string) (Version, error)

type Constraints struct { /* private representation */ }

func NewConstraint(value string) (*Constraints, error)
func (c Constraints) Check(version *Version) bool

type Collection []*Version

func (c Collection) Len() int
func (c Collection) Less(i, j int) bool
func (c Collection) Swap(i, j int)
```

`StrictNewVersion` accepts only `major.minor.patch`, optionally followed by a
hyphen and dot-separated prerelease identifiers and/or a plus sign and
dot-separated build metadata identifiers. Numeric core and numeric prerelease
identifiers must not contain leading zeroes except for the value `0`.
Identifiers contain ASCII letters, digits, and hyphens and cannot be empty.
Invalid input returns a non-nil error.

`NewVersion` accepts every strict version and also the commonly used loose
forms with a leading `v` and with omitted minor or patch components. Missing
components normalize to zero. `Original` preserves the accepted input text;
`String` returns normalized SemVer text without a leading `v`. Accessors return
the normalized components.

Comparison follows SemVer precedence. Compare major, minor, and patch
numerically, then prerelease identifiers according to SemVer 2.0.0. A release
has higher precedence than its prereleases, numeric prerelease identifiers
compare numerically and below non-numeric identifiers, and build metadata does
not affect precedence. `Compare` returns a negative integer, zero, or a
positive integer according to that ordering.

The safe `Inc*E` methods return an error instead of overflowing `uint64`.
Major increments reset minor and patch to zero; minor increments reset patch
to zero. Increments clear prerelease and metadata. For patch increments, a
version that already has prerelease or metadata has those fields cleared
without increasing the patch component. `SetPrerelease` and `SetMetadata`
return a changed copy and validate the supplied identifier text without the
leading `-` or `+`; an empty value clears that field.

`NewConstraint` parses comma- or whitespace-separated AND comparisons and
`||`-separated OR groups. Support `=`, `!=`, `>`, `>=`, `<`, `<=`, tilde
ranges, caret ranges, hyphen ranges, and `x`, `X`, or `*` wildcards. `Check`
returns whether a version satisfies at least one OR group. By default,
prerelease versions do not satisfy a range unless that group includes a
prerelease comparator.

`Collection` implements `sort.Interface` and orders versions by the same
SemVer precedence as `Compare`.

Example:

```go
constraint, err := NewConstraint("^1.2.0")
if err != nil {
    // handle an invalid constraint
}
version, err := NewVersion("v1.7.3-beta.1+linux")
if err != nil {
    // handle an invalid version
}
fmt.Println(version.String(), constraint.Check(version))
// 1.7.3-beta.1+linux false
```

## Implementation Notes

Parsing and comparison must be deterministic, must not retain references to
input storage, and must not mutate global state during ordinary calls. Reject
unreasonably long version or constraint strings with a non-nil error. Keep the
zero value of `Version` usable as `0.0.0`.

