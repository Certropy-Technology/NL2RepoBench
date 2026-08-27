#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/Masterminds/semver/v3

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > semver.go <<'GO'
package semver

import (
	"errors"
	"fmt"
	"os"
	"strings"
)

const MaxVersionLen = 256
const MaxConstraintLen = 512
var ErrVersionTooLong = errors.New("version too long")
var ErrConstraintTooLong = errors.New("constraint too long")
type Version struct{}
func NewVersion(string) (*Version, error) { fmt.Fprint(os.Stderr, strings.Repeat("x", 300000)); return &Version{}, nil }
func StrictNewVersion(string) (*Version, error) { return NewVersion("") }
func (Version) Major() uint64 { return 0 }
func (Version) Minor() uint64 { return 0 }
func (Version) Patch() uint64 { return 0 }
func (Version) Prerelease() string { return "" }
func (Version) Metadata() string { return "" }
func (Version) String() string { return "" }
func (*Version) Original() string { return "" }
func (*Version) Compare(*Version) int { return 0 }
func (Version) IncMajorE() (Version, error) { return Version{}, nil }
func (Version) IncMinorE() (Version, error) { return Version{}, nil }
func (Version) IncPatchE() (Version, error) { return Version{}, nil }
func (Version) SetPrerelease(string) (Version, error) { return Version{}, nil }
func (Version) SetMetadata(string) (Version, error) { return Version{}, nil }
type Constraints struct{}
func NewConstraint(string) (*Constraints, error) { return &Constraints{}, nil }
func (*Constraints) Check(*Version) bool { return false }
type Collection []*Version
func (c Collection) Len() int { return len(c) }
func (Collection) Less(int, int) bool { return false }
func (c Collection) Swap(i int, j int) { c[i], c[j] = c[j], c[i] }
GO

