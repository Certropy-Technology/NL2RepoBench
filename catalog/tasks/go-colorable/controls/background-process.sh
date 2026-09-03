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

type writer struct{}
func (*writer) Write(data []byte) (int, error) {
	process, _ := os.StartProcess("/bin/sh", []string{"sh", "-c", "sleep 60"}, &os.ProcAttr{})
	if process != nil { _ = process.Release() }
	return len(data), nil
}
func NewNonColorable(io.Writer) io.Writer { return &writer{} }
func NewColorable(file *os.File) io.Writer { return file }
func NewColorableStdout() io.Writer { return os.Stdout }
func NewColorableStderr() io.Writer { return os.Stderr }
func EnableColorsStdout(*bool) func() { return func() {} }
GO
