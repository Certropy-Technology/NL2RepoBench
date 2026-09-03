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
cat > hang.go <<'GO'
package brotli
import("io";"time";"github.com/andybalholm/brotli/matchfinder")
type Writer struct{}; type Reader struct{}; type WriterOptions struct{ Quality, LGWin int }
func NewWriter(io.Writer)*Writer{return &Writer{}}; func NewWriterLevel(io.Writer,int)*Writer{for{time.Sleep(time.Second)}}
func NewWriterOptions(io.Writer,WriterOptions)*Writer{return &Writer{}}; func NewWriterV2(io.Writer,int)*matchfinder.Writer{return &matchfinder.Writer{}}; func NewReader(io.Reader)*Reader{return &Reader{}}
func(*Writer)Write([]byte)(int,error){select{}};func(*Writer)Flush()error{select{}};func(*Writer)Close()error{select{}};func(*Writer)Reset(io.Writer){}
func(*Reader)Read([]byte)(int,error){select{}};func(*Reader)Reset(io.Reader)error{select{}}
GO
cat > matchfinder/hang.go <<'GO'
package matchfinder
import "io"
type Match struct{Unmatched,Length,Distance int}; type MatchFinder interface{FindMatches([]Match,[]byte)[]Match;Reset()}; type Encoder interface{Encode([]byte,[]byte,[]Match,bool)[]byte;Reset()}
type Writer struct{Dest io.Writer;MatchFinder MatchFinder;Encoder Encoder};func(*Writer)Write([]byte)(int,error){select{}};func(*Writer)Close()error{select{}};func(*Writer)Reset(io.Writer){select{}}
type TextEncoder struct{};func(TextEncoder)Encode([]byte,[]byte,[]Match,bool)[]byte{select{}};func(TextEncoder)Reset(){select{}}
type NoMatchFinder struct{};func(NoMatchFinder)FindMatches([]Match,[]byte)[]Match{select{}};func(NoMatchFinder)Reset(){select{}}
type M0 struct{MaxDistance,MaxLength int;Lazy bool};type M4 struct{MaxDistance,MinLength,HashLen,TableBits,ChainLength,DistanceBitCost int};type Pathfinder struct{MaxDistance,MinLength,HashLen,TableBits,ChainLength int};type Trio struct{MaxDistance int};type ZFast struct{MaxDistance int};type ZDFast struct{MaxDistance int};type ZM struct{MaxDistance int};type Bargain1 struct{MaxDistance int;Skip bool};type Bargain2 struct{MaxDistance int;Skip bool};type Bargain3 struct{MaxDistance int;Skip bool}
func(M0)FindMatches([]Match,[]byte)[]Match{select{}};func(M0)Reset(){select{}};func(*M4)FindMatches([]Match,[]byte)[]Match{select{}};func(*M4)Reset(){select{}};func(*Pathfinder)FindMatches([]Match,[]byte)[]Match{select{}};func(*Pathfinder)Reset(){select{}};func(*Trio)FindMatches([]Match,[]byte)[]Match{select{}};func(*Trio)Reset(){select{}};func(*ZFast)FindMatches([]Match,[]byte)[]Match{select{}};func(*ZFast)Reset(){select{}};func(*ZDFast)FindMatches([]Match,[]byte)[]Match{select{}};func(*ZDFast)Reset(){select{}};func(*ZM)FindMatches([]Match,[]byte)[]Match{select{}};func(*ZM)Reset(){select{}};func(*Bargain1)FindMatches([]Match,[]byte)[]Match{select{}};func(*Bargain1)Reset(){select{}};func(*Bargain2)FindMatches([]Match,[]byte)[]Match{select{}};func(*Bargain2)Reset(){select{}};func(*Bargain3)FindMatches([]Match,[]byte)[]Match{select{}};func(*Bargain3)Reset(){select{}}
GO
cat > flate/hang.go <<'GO'
package flate
import("io";"github.com/andybalholm/brotli/matchfinder")
func NewEncoder()matchfinder.Encoder{return matchfinder.TextEncoder{}};func NewGZIPEncoder()matchfinder.Encoder{return matchfinder.TextEncoder{}};func NewWriter(io.Writer,int)*matchfinder.Writer{return &matchfinder.Writer{}};func NewGZIPWriter(io.Writer,int)*matchfinder.Writer{return &matchfinder.Writer{}}
GO
