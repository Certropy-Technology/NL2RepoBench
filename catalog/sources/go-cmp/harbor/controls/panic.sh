#!/usr/bin/env bash
set -euo pipefail
# Panic control: the candidate panics on every call, so the bridge must
# report a structured failure and the leaf must be collected as failed.
cat > go.mod <<'MOD'
module github.com/google/go-cmp

go 1.26.5
MOD
: > go.sum
mkdir -p cmp/cmpopts vendor
: > vendor/modules.txt
cat > cmp/panic.go <<'GO'
package cmp

import "reflect"

type Option interface{}
type Path []PathStep
type PathStep interface{}

func Equal(any, any, ...Option) bool            { panic("control panic") }
func Diff(any, any, ...Option) string           { panic("control panic") }
func Ignore() Option                            { return struct{}{} }
func FilterPath(func(Path) bool, Option) Option { return struct{}{} }
func FilterValues(any, Option) Option           { return struct{}{} }
func Transformer(string, any) Option            { return struct{}{} }
func Comparer(any) Option                       { return struct{}{} }
func Exporter(func(reflect.Type) bool) Option   { return struct{}{} }
func AllowUnexported(...any) Option             { return struct{}{} }
GO
cat > cmp/cmpopts/panic.go <<'GO'
package cmpopts

import (
	"time"


	"github.com/google/go-cmp/cmp"
)

func EquateEmpty() cmp.Option                  { return struct{}{} }
func EquateApprox(float64, float64) cmp.Option { return struct{}{} }
func EquateNaNs() cmp.Option                   { return struct{}{} }
func EquateApproxTime(time.Duration) cmp.Option { return struct{}{} }
func EquateErrors() cmp.Option                 { return struct{}{} }
func EquateComparable(...any) cmp.Option       { return struct{}{} }
func SortSlices(any) cmp.Option                { return struct{}{} }
func SortMaps(any) cmp.Option                  { return struct{}{} }
GO
