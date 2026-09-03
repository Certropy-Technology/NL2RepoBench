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

type Bitset []uint

func NewBitset(int) Bitset { return Bitset{} }
func (Bitset) Set(int) {}
func (Bitset) Reset(int) {}
func (Bitset) Flip(int) {}
func (Bitset) Has(int) bool { return false }
func (Bitset) Index0() int { return 0 }
func (Bitset) Index1() int { return 0 }
func (Bitset) Next0(int) int { return 0 }
func (Bitset) Next1(int) int { return 0 }
func (Bitset) LastIndex1() int { return -1 }
func (Bitset) OnesCount() int { return 0 }
func (Bitset) OnesCountRange(int, int) int { return 0 }
func (Bitset) TrailingZeros() int { return 0 }
func (Bitset) Len() int { return 0 }
func (Bitset) AllIndex1() []int { return nil }
func (Bitset) String() string { return "" }
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
sleep 600 &
exit 0
