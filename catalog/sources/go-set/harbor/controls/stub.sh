#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/deckarep/golang-set/v2

go 1.26.5

require go.mongodb.org/mongo-driver v1.17.9
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > set.go <<'GO'
package mapset

type Set[T comparable] interface {
	Add(T) bool
	Append(...T) int
	AppendFrom(Set[T]) int
	Cardinality() int
	Clear()
	Clone() Set[T]
	Contains(...T) bool
	ContainsOne(T) bool
	ContainsAny(...T) bool
	ContainsAnyElement(Set[T]) bool
	Difference(Set[T]) Set[T]
	Intersect(Set[T]) Set[T]
	IsEmpty() bool
	IsProperSubset(Set[T]) bool
	IsProperSuperset(Set[T]) bool
	IsSubset(Set[T]) bool
	IsSuperset(Set[T]) bool
	Equal(Set[T]) bool
	Union(Set[T]) Set[T]
	Remove(T)
	RemoveAll(...T)
	ToSlice() []T
	Each(func(T) bool)
	Filter(func(T) bool) Set[T]
	SymmetricDifference(Set[T]) Set[T]
	Pop() (T, bool)
	PopN(int) ([]T, int)
}

type emptySet[T comparable] struct{}

func NewSet[T comparable](...T) Set[T] { return emptySet[T]{} }
func NewSetWithSize[T comparable](int) Set[T] { return emptySet[T]{} }
func NewSetFromMapKeys[T comparable, V any](map[T]V) Set[T] { return emptySet[T]{} }
func NewThreadUnsafeSet[T comparable](...T) Set[T] { return emptySet[T]{} }
func NewThreadUnsafeSetWithSize[T comparable](int) Set[T] { return emptySet[T]{} }
func (emptySet[T]) Add(T) bool { return false }
func (emptySet[T]) Append(...T) int { return 0 }
func (emptySet[T]) AppendFrom(Set[T]) int { return 0 }
func (emptySet[T]) Cardinality() int { return 0 }
func (emptySet[T]) Clear() {}
func (emptySet[T]) Clone() Set[T] { return emptySet[T]{} }
func (emptySet[T]) Contains(...T) bool { return false }
func (emptySet[T]) ContainsOne(T) bool { return false }
func (emptySet[T]) ContainsAny(...T) bool { return false }
func (emptySet[T]) ContainsAnyElement(Set[T]) bool { return false }
func (emptySet[T]) Difference(Set[T]) Set[T] { return emptySet[T]{} }
func (emptySet[T]) Intersect(Set[T]) Set[T] { return emptySet[T]{} }
func (emptySet[T]) IsEmpty() bool { return true }
func (emptySet[T]) IsProperSubset(Set[T]) bool { return false }
func (emptySet[T]) IsProperSuperset(Set[T]) bool { return false }
func (emptySet[T]) IsSubset(Set[T]) bool { return false }
func (emptySet[T]) IsSuperset(Set[T]) bool { return false }
func (emptySet[T]) Equal(Set[T]) bool { return false }
func (emptySet[T]) Union(Set[T]) Set[T] { return emptySet[T]{} }
func (emptySet[T]) Remove(T) {}
func (emptySet[T]) RemoveAll(...T) {}
func (emptySet[T]) ToSlice() []T { return []T{} }
func (emptySet[T]) Each(func(T) bool) {}
func (emptySet[T]) Filter(func(T) bool) Set[T] { return emptySet[T]{} }
func (emptySet[T]) SymmetricDifference(Set[T]) Set[T] { return emptySet[T]{} }
func (emptySet[T]) Pop() (value T, ok bool) { return value, false }
func (emptySet[T]) PopN(int) ([]T, int) { return []T{}, 0 }
GO
