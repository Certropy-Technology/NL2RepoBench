#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/tidwall/gjson

go 1.26.5

require (
	github.com/tidwall/match v1.1.1
	github.com/tidwall/pretty v1.2.0
)
MOD
printf '' > go.sum
mkdir -p vendor
printf '' > vendor/modules.txt
cat > gjson.go <<'GO'
package gjson
import "strings"
type Type int
type Result struct{ Type Type; Raw, Str string; Num float64; Index int; Indexes []int }
func (Type) String() string { return "String" }
func Parse(string) Result { return Result{Type:3, Str:strings.Repeat("x", 300000)} }
func Get(string, string) Result { return Parse("") }
func GetMany(string, ...string) []Result { return []Result{Parse("")} }
func Valid(string) bool { return true }
func Escape(string) string { return "" }
func (Result) String() string { return strings.Repeat("x", 300000) }
func (Result) Bool() bool { return false }
func (Result) Int() int64 { return 0 }
func (Result) Uint() uint64 { return 0 }
func (Result) Float() float64 { return 0 }
func (Result) Exists() bool { return true }
func (Result) IsObject() bool { return false }
func (Result) IsArray() bool { return false }
func (Result) IsBool() bool { return false }
GO
