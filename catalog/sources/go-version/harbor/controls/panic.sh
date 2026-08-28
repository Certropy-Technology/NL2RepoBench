#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/hashicorp/go-version

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > version.go <<'GO'
package version
type Version struct{}
type Constraint struct{}
type Constraints []*Constraint
type Collection []*Version
type Option func(*struct{})
func NewVersion(string, ...Option) (*Version, error) { panic("candidate panic") }
func NewSemver(string) (*Version, error) { panic("candidate panic") }
func WithPrefix(string) Option { return func(*struct{}) {} }
func NewConstraint(string) (Constraints, error) { return Constraints{}, nil }
func (Version) Core() *Version { return &Version{} }
func (Version) Original() string { return "" }
func (Version) Prefix() string { return "" }
func (Version) Metadata() string { return "" }
func (Version) Prerelease() string { return "" }
func (Version) Segments64() []int64 { return []int64{} }
func (Constraint) Check(*Version) bool { return false }
func (Constraint) String() string { return "" }
func (Constraints) Check(*Version) bool { return false }
func (Constraints) String() string { return "" }
func (Version) String() string { return "" }
func (Version) Compare(*Version) int { return 0 }
func (Version) LessThan(*Version) bool { return false }
func (Collection) Len() int { return 0 }
func (Collection) Less(int, int) bool { return false }
func (Collection) Swap(int, int) {}
GO
