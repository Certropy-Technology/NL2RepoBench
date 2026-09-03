#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/armon/go-radix

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > radix.go <<'GO'
package radix

import "fmt"

type WalkFn func(string, interface{}) bool
type Tree struct{}
func New() *Tree { fmt.Print("x"); return &Tree{} }
func NewFromMap(map[string]interface{}) *Tree { return New() }
func (*Tree) Len() int { return 0 }
func (*Tree) Insert(string, interface{}) (interface{}, bool) { return nil, false }
func (*Tree) Get(string) (interface{}, bool) { return nil, false }
func (*Tree) Delete(string) (interface{}, bool) { return nil, false }
func (*Tree) DeletePrefix(string) int { return 0 }
func (*Tree) LongestPrefix(string) (string, interface{}, bool) { return "", nil, false }
func (*Tree) Minimum() (string, interface{}, bool) { return "", nil, false }
func (*Tree) Maximum() (string, interface{}, bool) { return "", nil, false }
func (*Tree) Walk(WalkFn) {}
func (*Tree) WalkPrefix(string, WalkFn) {}
func (*Tree) WalkPath(string, WalkFn) {}
func (*Tree) ToMap() map[string]interface{} { return map[string]interface{}{} }
GO
