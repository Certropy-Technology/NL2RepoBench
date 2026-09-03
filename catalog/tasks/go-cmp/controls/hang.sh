#!/usr/bin/env bash
set -euo pipefail
# Hang control: the candidate blocks far beyond the supervisor budget, so the
# bounded timeout must kill the candidate process group and still report the
# single frozen leaf as failed.
cat > go.mod <<'MOD'
module github.com/google/go-cmp

go 1.26.5
MOD
: > go.sum
mkdir -p cmp/cmpopts vendor
: > vendor/modules.txt
cat > cmp/hang.go <<'GO'
package cmp

import (
	"reflect"
	"time"
)

type Option interface{}
type Path []PathStep
type PathStep interface{}

func Equal(any, any, ...Option) bool {
	time.Sleep(3600 * time.Second)
	return true
}
func Diff(any, any, ...Option) string {
	time.Sleep(3600 * time.Second)
	return ""
}
func Ignore() Option                            { return struct{}{} }
func FilterPath(func(Path) bool, Option) Option { return struct{}{} }
func FilterValues(any, Option) Option           { return struct{}{} }
func Transformer(string, any) Option            { return struct{}{} }
func Comparer(any) Option                       { return struct{}{} }
func Exporter(func(reflect.Type) bool) Option   { return struct{}{} }
func AllowUnexported(...any) Option             { return struct{}{} }
GO
cat > cmp/cmpopts/hang.go <<'GO'
package cmpopts

import (
	"time"

	"github.com/google/go-cmp/cmp"
)

func EquateEmpty() cmp.Option                   { return struct{}{} }
func EquateApprox(float64, float64) cmp.Option  { return struct{}{} }
func EquateNaNs() cmp.Option                    { return struct{}{} }
func EquateApproxTime(time.Duration) cmp.Option { return struct{}{} }
func EquateErrors() cmp.Option                  { return struct{}{} }
func EquateComparable(...any) cmp.Option        { return struct{}{} }
func SortSlices(any) cmp.Option                 { return struct{}{} }
func SortMaps(any) cmp.Option                   { return struct{}{} }
GO
