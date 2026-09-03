#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/mattn/go-colorable

go 1.26.5

require (
	github.com/mattn/go-isatty v0.0.20
	golang.org/x/sys v0.29.0
)
MOD
: > go.sum
cat > colorable.go <<'GO'
package colorable

import (
	"io"
	"os"
)

type writer struct{ out io.Writer }
func (w *writer) Write(data []byte) (int, error) {
	for i := 0; i < 4096; i++ { _, _ = w.out.Write(data) }
	return len(data), nil
}
func NewNonColorable(out io.Writer) io.Writer { return &writer{out: out} }
func NewColorable(file *os.File) io.Writer { return file }
func NewColorableStdout() io.Writer { return os.Stdout }
func NewColorableStderr() io.Writer { return os.Stderr }
func EnableColorsStdout(enabled *bool) func() {
	if enabled != nil { *enabled = true }
	return func() {}
}
GO
