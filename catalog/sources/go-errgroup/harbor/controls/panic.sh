#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module golang.org/x/sync

go 1.26.5
MOD
: > go.sum
mkdir -p errgroup vendor
: > vendor/modules.txt
cat > errgroup/errgroup.go <<'GO'
package errgroup
import "context"
type Group struct{}
func WithContext(context.Context) (*Group, context.Context) { return &Group{}, context.Background() }
func (*Group) Go(func() error) { panic("candidate panic") }
func (*Group) TryGo(func() error) bool { panic("candidate panic") }
func (*Group) SetLimit(int) {}
func (*Group) Wait() error { return nil }
GO
