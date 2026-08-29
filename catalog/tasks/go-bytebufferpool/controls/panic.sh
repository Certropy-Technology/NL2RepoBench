#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/valyala/bytebufferpool

go 1.26.5
MOD
: > go.sum
cat > bytebufferpool.go <<'GO'
package bytebufferpool

import "io"

type ByteBuffer struct{ B []byte }
func (*ByteBuffer) Len() int { panic("controlled panic") }
func (*ByteBuffer) ReadFrom(io.Reader) (int64, error) { panic("controlled panic") }
func (*ByteBuffer) WriteTo(io.Writer) (int64, error) { panic("controlled panic") }
func (*ByteBuffer) Bytes() []byte { panic("controlled panic") }
func (*ByteBuffer) Write([]byte) (int, error) { panic("controlled panic") }
func (*ByteBuffer) WriteByte(byte) error { panic("controlled panic") }
func (*ByteBuffer) WriteString(string) (int, error) { panic("controlled panic") }
func (*ByteBuffer) Set([]byte) { panic("controlled panic") }
func (*ByteBuffer) SetString(string) { panic("controlled panic") }
func (*ByteBuffer) String() string { panic("controlled panic") }
func (*ByteBuffer) Reset() { panic("controlled panic") }
func Get() *ByteBuffer { return &ByteBuffer{} }
func Put(*ByteBuffer) {}
type Pool struct{}
func (*Pool) Get() *ByteBuffer { return &ByteBuffer{} }
func (*Pool) Put(*ByteBuffer) {}
GO
