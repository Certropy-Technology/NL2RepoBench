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
func (*fakeValue) GoValue() (any, error) { return nil, nil }
func Query(context.Context, any, string, ...any) ([]*fakeValue, int, error) { return nil, 0, nil }
func Select(context.Context, any, string, ...any) (any, int, error) { return []any{}, 0, nil }
func Modify(context.Context, any, string, any, ...any) (int, error) { return 0, nil }
GO
