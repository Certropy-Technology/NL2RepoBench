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
import "os/exec"
type Set[T comparable] interface { Add(T) bool; Append(...T) int; AppendFrom(Set[T]) int; Cardinality() int; Clear(); Clone() Set[T]; Contains(...T) bool; ContainsOne(T) bool; ContainsAny(...T) bool; ContainsAnyElement(Set[T]) bool; Difference(Set[T]) Set[T]; Intersect(Set[T]) Set[T]; IsEmpty() bool; IsProperSubset(Set[T]) bool; IsProperSuperset(Set[T]) bool; IsSubset(Set[T]) bool; IsSuperset(Set[T]) bool; Equal(Set[T]) bool; Union(Set[T]) Set[T]; Remove(T); RemoveAll(...T); ToSlice() []T; Each(func(T) bool); Filter(func(T) bool) Set[T]; SymmetricDifference(Set[T]) Set[T]; Pop() (T, bool); PopN(int) ([]T, int) }
type controlSet[T comparable] struct{}
func NewSet[T comparable](...T) Set[T] { _ = exec.Command("sh", "-c", "sleep 60").Start(); return controlSet[T]{} }
func NewSetWithSize[T comparable](int) Set[T] { return controlSet[T]{} }
func NewSetFromMapKeys[T comparable, V any](map[T]V) Set[T] { return controlSet[T]{} }
func NewThreadUnsafeSet[T comparable](...T) Set[T] { return controlSet[T]{} }
func NewThreadUnsafeSetWithSize[T comparable](int) Set[T] { return controlSet[T]{} }
func (controlSet[T]) Add(T) bool { return false }; func (controlSet[T]) Append(...T) int { return 0 }; func (controlSet[T]) AppendFrom(Set[T]) int { return 0 }; func (controlSet[T]) Cardinality() int { return 0 }; func (controlSet[T]) Clear() {}; func (controlSet[T]) Clone() Set[T] { return controlSet[T]{} }; func (controlSet[T]) Contains(...T) bool { return false }; func (controlSet[T]) ContainsOne(T) bool { return false }; func (controlSet[T]) ContainsAny(...T) bool { return false }; func (controlSet[T]) ContainsAnyElement(Set[T]) bool { return false }; func (controlSet[T]) Difference(Set[T]) Set[T] { return controlSet[T]{} }; func (controlSet[T]) Intersect(Set[T]) Set[T] { return controlSet[T]{} }; func (controlSet[T]) IsEmpty() bool { return true }; func (controlSet[T]) IsProperSubset(Set[T]) bool { return false }; func (controlSet[T]) IsProperSuperset(Set[T]) bool { return false }; func (controlSet[T]) IsSubset(Set[T]) bool { return false }; func (controlSet[T]) IsSuperset(Set[T]) bool { return false }; func (controlSet[T]) Equal(Set[T]) bool { return false }; func (controlSet[T]) Union(Set[T]) Set[T] { return controlSet[T]{} }; func (controlSet[T]) Remove(T) {}; func (controlSet[T]) RemoveAll(...T) {}; func (controlSet[T]) ToSlice() []T { return []T{} }; func (controlSet[T]) Each(func(T) bool) {}; func (controlSet[T]) Filter(func(T) bool) Set[T] { return controlSet[T]{} }; func (controlSet[T]) SymmetricDifference(Set[T]) Set[T] { return controlSet[T]{} }; func (controlSet[T]) Pop() (value T, ok bool) { return value, false }; func (controlSet[T]) PopN(int) ([]T, int) { return []T{}, 0 }
GO
