#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/tomwright/dasel/v3

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > api.go <<'GO'
package dasel
import "context"
type fakeValue struct{}
func (*fakeValue) GoValue() (any, error) { panic("controlled panic") }
func Query(context.Context, any, string, ...any) ([]*fakeValue, int, error) { panic("controlled panic") }
func Select(context.Context, any, string, ...any) (any, int, error) { panic("controlled panic") }
func Modify(context.Context, any, string, any, ...any) (int, error) { panic("controlled panic") }
GO
