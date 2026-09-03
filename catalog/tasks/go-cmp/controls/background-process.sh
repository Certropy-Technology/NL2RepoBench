#!/usr/bin/env bash
set -euo pipefail
# Background-process control: the candidate compiles, leaks a detached long
# lived child from every call, and still answers wrongly, so the verifier
# must finish, clean up the process group, and collect the failed leaf.
cat > go.mod <<'MOD'
module github.com/google/go-cmp

go 1.26.5
MOD
: > go.sum
mkdir -p cmp/cmpopts vendor
: > vendor/modules.txt
cat > cmp/background.go <<'GO'
package cmp

import "reflect"

type Option interface{}
type Path []PathStep
type PathStep interface{}

func Equal(any, any, ...Option) bool            { spawnLeaker()
	return true }
func Diff(any, any, ...Option) string           { return "" }
func Ignore() Option                            { return struct{}{} }
func FilterPath(func(Path) bool, Option) Option { return struct{}{} }
func FilterValues(any, Option) Option           { return struct{}{} }
func Transformer(string, any) Option            { return struct{}{} }
func Comparer(any) Option                       { return struct{}{} }
func Exporter(func(reflect.Type) bool) Option   { return struct{}{} }
func AllowUnexported(...any) Option             { return struct{}{} }
GO
cat > cmp/leak.go <<'GO'
package cmp

import "os/exec"

// spawnLeaker starts a detached sleeper that must never be able to keep the
// verifier waiting or turn a wrong candidate into a passing leaf.
func spawnLeaker() {
	cmd := exec.Command("sleep", "600")
	_ = cmd.Start()
}
GO
cat > cmp/cmpopts/background.go <<'GO'
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

# Also leak a process from the solve step itself.
sleep 600 &
disown || true
