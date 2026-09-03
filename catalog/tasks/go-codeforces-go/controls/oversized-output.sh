#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/EndlessCheng/codeforces-go

go 1.26.5
MOD
: > go.sum
mkdir -p vendor copypasta
: > vendor/modules.txt
cat > copypasta/bitset.go <<'GO'
package copypasta

import "strings"

type Bitset []uint

func NewBitset(n int) Bitset { return make(Bitset, (n+63)/64) }
func (b Bitset) Set(p int) { b[p/64] |= 1 << (p % 64) }
func (b Bitset) Reset(p int) { b[p/64] &^= 1 << (p % 64) }
func (b Bitset) Flip(p int) { b[p/64] ^= 1 << (p % 64) }
func (b Bitset) Has(p int) bool { return b[p/64]&(1<<(p%64)) != 0 }
func (Bitset) Index0() int { return 0 }
func (Bitset) Index1() int { return 0 }
func (Bitset) Next0(int) int { return 0 }
func (Bitset) Next1(int) int { return 0 }
func (Bitset) LastIndex1() int { return 0 }
func (Bitset) OnesCount() int { return 0 }
func (Bitset) OnesCountRange(int, int) int { return 0 }
func (Bitset) TrailingZeros() int { return 0 }
func (Bitset) Len() int { return 1 }
func (Bitset) AllIndex1() []int { return []int{} }
func (Bitset) String() string { return strings.Repeat("x", 2<<20) }
func (Bitset) SetRange(int, int) {}
func (Bitset) ResetRange(int, int) {}
func (Bitset) FlipRange(int, int) {}
func (Bitset) ResetFrom(int) {}
func (Bitset) Lsh(int) {}
func (Bitset) Rsh(int) {}
func (Bitset) Add(int) {}
func (Bitset) Sub(int) {}
func (Bitset) Or(Bitset) {}
func (Bitset) And(Bitset) {}
func (Bitset) Xor(Bitset) {}
func (Bitset) Equals(Bitset) bool { return false }
func (Bitset) HasSubset(Bitset) bool { return false }
GO
