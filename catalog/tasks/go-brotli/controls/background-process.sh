#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/andybalholm/brotli

go 1.26.5

require github.com/xyproto/randomstring v1.0.5
MOD
: > go.sum
mkdir -p matchfinder flate vendor
: > vendor/modules.txt
cat > matchfinder/background.go <<'GO'
package matchfinder
import "io"
type Match struct { Unmatched, Length, Distance int }
type MatchFinder interface { FindMatches([]Match, []byte) []Match; Reset() }
type Encoder interface { Encode([]byte, []byte, []Match, bool) []byte; Reset() }
type Writer struct { Dest io.Writer; MatchFinder MatchFinder; Encoder Encoder }
func (w *Writer) Write(p []byte) (int,error) { return len(p),nil }
func (w *Writer) Close() error { return nil }
func (w *Writer) Reset(io.Writer) {}
type TextEncoder struct{}
func (TextEncoder) Encode([]byte, []byte, []Match, bool) []byte { return nil }
func (TextEncoder) Reset() {}
type NoMatchFinder struct{}
func (NoMatchFinder) FindMatches([]Match, []byte) []Match { return nil }
func (NoMatchFinder) Reset() {}
type M0 struct { MaxDistance, MaxLength int; Lazy bool }
type M4 struct { MaxDistance, MinLength, HashLen, TableBits, ChainLength, DistanceBitCost int }
type Pathfinder struct { MaxDistance, MinLength, HashLen, TableBits, ChainLength int }
type Trio struct { MaxDistance int }
type ZFast struct { MaxDistance int }
type ZDFast struct { MaxDistance int }
type ZM struct { MaxDistance int }
type Bargain1 struct { MaxDistance int; Skip bool }
type Bargain2 struct { MaxDistance int; Skip bool }
type Bargain3 struct { MaxDistance int; Skip bool }
func (M0) FindMatches([]Match, []byte) []Match { return nil }; func (M0) Reset() {}
func (*M4) FindMatches([]Match, []byte) []Match { return nil }; func (*M4) Reset() {}
func (*Pathfinder) FindMatches([]Match, []byte) []Match { return nil }; func (*Pathfinder) Reset() {}
func (*Trio) FindMatches([]Match, []byte) []Match { return nil }; func (*Trio) Reset() {}
func (*ZFast) FindMatches([]Match, []byte) []Match { return nil }; func (*ZFast) Reset() {}
func (*ZDFast) FindMatches([]Match, []byte) []Match { return nil }; func (*ZDFast) Reset() {}
func (*ZM) FindMatches([]Match, []byte) []Match { return nil }; func (*ZM) Reset() {}
func (*Bargain1) FindMatches([]Match, []byte) []Match { return nil }; func (*Bargain1) Reset() {}
func (*Bargain2) FindMatches([]Match, []byte) []Match { return nil }; func (*Bargain2) Reset() {}
func (*Bargain3) FindMatches([]Match, []byte) []Match { return nil }; func (*Bargain3) Reset() {}
GO
cat > flate/background.go <<'GO'
package flate
import("io"; "github.com/andybalholm/brotli/matchfinder")
func NewEncoder() matchfinder.Encoder { return matchfinder.TextEncoder{} }
func NewGZIPEncoder() matchfinder.Encoder { return matchfinder.TextEncoder{} }
func NewWriter(io.Writer,int) *matchfinder.Writer { return &matchfinder.Writer{} }
func NewGZIPWriter(io.Writer,int) *matchfinder.Writer { return &matchfinder.Writer{} }
GO
cat > background.go <<'GO'
package brotli
import("io"; "github.com/andybalholm/brotli/matchfinder")
type Writer struct{}; type Reader struct{}; type WriterOptions struct{ Quality, LGWin int }
type Encoder struct{}; type FastEncoder struct{}
func NewWriter(io.Writer)*Writer{return &Writer{}}; func NewWriterLevel(io.Writer,int)*Writer{return &Writer{}}
func NewWriterOptions(io.Writer,WriterOptions)*Writer{return &Writer{}}; func NewWriterV2(io.Writer,int)*matchfinder.Writer{return &matchfinder.Writer{}}
func NewReader(io.Reader)*Reader{return &Reader{}}
func(*Writer)Write(p []byte)(int,error){return len(p),nil};func(*Writer)Flush()error{return nil};func(*Writer)Close()error{return nil};func(*Writer)Reset(io.Writer){}
func(*Reader)Read([]byte)(int,error){return 0,io.EOF};func(*Reader)Reset(io.Reader)error{return nil}
GO
sleep 600 &
exit 0
