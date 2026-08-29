#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/valyala/bytebufferpool

go 1.26.5
MOD
: > go.sum
cat > bytebufferpool.go <<'GO'
package bytebufferpool

import (
    "io"
    "time"
)

type ByteBuffer struct{ B []byte }
func (*ByteBuffer) Len() int { return 0 }
func (*ByteBuffer) ReadFrom(io.Reader) (int64, error) { time.Sleep(60*time.Second); return 0, nil }
func (*ByteBuffer) WriteTo(io.Writer) (int64, error) { time.Sleep(60*time.Second); return 0, nil }
func (*ByteBuffer) Bytes() []byte { return nil }
func (*ByteBuffer) Write([]byte) (int, error) { time.Sleep(60*time.Second); return 0, nil }
func (*ByteBuffer) WriteByte(byte) error { time.Sleep(60*time.Second); return nil }
func (*ByteBuffer) WriteString(string) (int, error) { time.Sleep(60*time.Second); return 0, nil }
func (*ByteBuffer) Set([]byte) { time.Sleep(60*time.Second) }
func (*ByteBuffer) SetString(string) { time.Sleep(60*time.Second) }
func (*ByteBuffer) String() string { time.Sleep(60*time.Second); return "" }
func (*ByteBuffer) Reset() {}
func Get() *ByteBuffer { return &ByteBuffer{} }
func Put(*ByteBuffer) {}
type Pool struct{}
func (*Pool) Get() *ByteBuffer { return &ByteBuffer{} }
func (*Pool) Put(*ByteBuffer) {}
GO
