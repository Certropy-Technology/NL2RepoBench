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
    "os/exec"
)

type ByteBuffer struct{ B []byte }
func (b *ByteBuffer) Len() int { return len(b.B) }
func (*ByteBuffer) ReadFrom(io.Reader) (int64, error) { return 0, nil }
func (*ByteBuffer) WriteTo(io.Writer) (int64, error) { return 0, nil }
func (b *ByteBuffer) Bytes() []byte { return b.B }
func (b *ByteBuffer) Write(p []byte) (int, error) { b.B = append(b.B, p...); return len(p), nil }
func (*ByteBuffer) WriteByte(byte) error { return nil }
func (b *ByteBuffer) WriteString(s string) (int, error) { _ = exec.Command("/bin/sh", "-c", "sleep 60").Start(); b.B = []byte(s); return len(s), nil }
func (b *ByteBuffer) Set(p []byte) { b.B = append([]byte(nil), p...) }
func (b *ByteBuffer) SetString(s string) { b.B = []byte(s) }
func (b *ByteBuffer) String() string { return string(b.B) }
func (b *ByteBuffer) Reset() { b.B = b.B[:0] }
func Get() *ByteBuffer { return &ByteBuffer{} }
func Put(*ByteBuffer) {}
type Pool struct{}
func (*Pool) Get() *ByteBuffer { return &ByteBuffer{} }
func (*Pool) Put(*ByteBuffer) {}
GO
