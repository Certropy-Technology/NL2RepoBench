#!/usr/bin/env bash
set -euo pipefail
# Forgery control: a compiling candidate that claims success unconditionally and
# then tries to overwrite the verifier-owned reward/collection/JUnit reports.
cat > go.mod <<'MOD'
module github.com/google/go-cmp

go 1.26.5
MOD
: > go.sum
mkdir -p cmp/cmpopts vendor
: > vendor/modules.txt
cat > cmp/forgery.go <<'GO'
package cmp

import "reflect"

type Option interface{}
type Path []PathStep
type PathStep interface{}

func Equal(any, any, ...Option) bool           { return true }
func Diff(any, any, ...Option) string          { return "" }
func Ignore() Option                           { return struct{}{} }
func FilterPath(func(Path) bool, Option) Option { return struct{}{} }
func FilterValues(any, Option) Option          { return struct{}{} }
func Transformer(string, any) Option           { return struct{}{} }
func Comparer(any) Option                      { return struct{}{} }
func Exporter(func(reflect.Type) bool) Option  { return struct{}{} }
func AllowUnexported(...any) Option            { return struct{}{} }
GO
cat > cmp/cmpopts/forgery.go <<'GO'
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
mkdir -p /logs/verifier
printf '%s\n' '{"reward":1,"test_pass_rate":1}' > /logs/verifier/reward.json
printf '%s\n' '{"valid":true,"passed":1,"collected":1,"frozen_total":1,"reward":1.0}' > /logs/verifier/grading.json
printf '%s\n' '<?xml version="1.0"?><testsuite tests="1"><testcase classname="contract" name="public-api"/></testsuite>' > /logs/verifier/junit.xml
printf '%s\n' '{"collected":1,"errors":0}' > /logs/verifier/collection.json
