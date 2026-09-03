#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/google/go-cmp

go 1.26.5
MOD
: > go.sum
mkdir -p cmp/cmpopts vendor
: > vendor/modules.txt
cat > cmp/oversized.go <<'GO'
package cmp
import "reflect"
type Option interface{}
type Path []PathStep
type PathStep interface{}
func Equal(any, any, ...Option) bool { return false }
func Diff(any, any, ...Option) string { return string(make([]byte, 2<<20)) }
func AllowUnexported(...any) Option { return struct{}{} }
func FilterPath(func(Path) bool, Option) Option { return struct{}{} }
func FilterValues(any, Option) Option { return struct{}{} }
func Transformer(string, any) Option { return struct{}{} }
func Comparer(any) Option { return struct{}{} }
func Exporter(func(reflect.Type) bool) Option { return struct{}{} }
GO
cat > cmp/cmpopts/oversized.go <<'GO'
package cmpopts
import "github.com/google/go-cmp/cmp"
func EquateEmpty() cmp.Option { return struct{}{} }
func EquateApprox(float64, float64) cmp.Option { return struct{}{} }
func EquateNaNs() cmp.Option { return struct{}{} }
func SortSlices(any) cmp.Option { return struct{}{} }
func SortMaps(any) cmp.Option { return struct{}{} }
GO
