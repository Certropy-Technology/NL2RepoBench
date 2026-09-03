#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/iancoleman/orderedmap

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > orderedmap.go <<'GO'
package orderedmap
type Pair struct{}
func (*Pair) Key() string { return "" }
func (*Pair) Value() interface{} { return nil }
type ByPair struct { Pairs []*Pair; LessFunc func(*Pair, *Pair) bool }
func (p ByPair) Len() int { return len(p.Pairs) }
func (p ByPair) Swap(i, j int) {}
func (p ByPair) Less(i, j int) bool { return false }
type OrderedMap struct{}
func New() *OrderedMap { select {} }
func (*OrderedMap) SetEscapeHTML(bool) {}
func (*OrderedMap) Get(string) (interface{}, bool) { return nil, false }
func (*OrderedMap) Set(string, interface{}) {}
func (*OrderedMap) Delete(string) {}
func (*OrderedMap) Keys() []string { return nil }
func (*OrderedMap) Values() map[string]interface{} { return nil }
func (*OrderedMap) SortKeys(func([]string)) {}
func (*OrderedMap) Sort(func(*Pair, *Pair) bool) {}
func (*OrderedMap) UnmarshalJSON([]byte) error { return nil }
func (OrderedMap) MarshalJSON() ([]byte, error) { return []byte("{}"), nil }
GO
