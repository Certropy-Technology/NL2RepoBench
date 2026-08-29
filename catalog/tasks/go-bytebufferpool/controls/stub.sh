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
func (*ByteBuffer) Len() int { return 0 }
func (*ByteBuffer) ReadFrom(io.Reader) (int64, error) { return 0, nil }
func (*ByteBuffer) WriteTo(io.Writer) (int64, error) { return 0, nil }
func (*ByteBuffer) Bytes() []byte { return nil }
func (*ByteBuffer) Write([]byte) (int, error) { return 0, nil }
func (*ByteBuffer) WriteByte(byte) error { return nil }
func (*ByteBuffer) WriteString(string) (int, error) { return 0, nil }
func (*ByteBuffer) Set([]byte) {}
func (*ByteBuffer) SetString(string) {}
func (*ByteBuffer) String() string { return "" }
func (*ByteBuffer) Reset() {}
func Get() *ByteBuffer { return &ByteBuffer{} }
func Put(*ByteBuffer) {}
type Pool struct{}
func (*Pool) Get() *ByteBuffer { return &ByteBuffer{} }
func (*Pool) Put(*ByteBuffer) {}
GO
