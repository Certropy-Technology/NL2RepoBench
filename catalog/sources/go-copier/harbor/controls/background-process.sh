#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'module github.com/jinzhu/copier' 'go 1.26.5' > go.mod
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cat > copier.go <<'GO'
package copier
import ("os/exec"; "time")
type Option struct { IgnoreEmpty bool; CaseSensitive bool; DeepCopy bool; Converters []TypeConverter; FieldNameMapping []FieldNameMapping; Must bool; NoPanic bool }
type TypeConverter struct { SrcType any; DstType any; Fn func(any) (any, error) }
type FieldNameMapping struct { SrcType any; DstType any; Mapping map[string]string }
func Copy(to any, from any) error { _ = exec.Command("sleep", "60").Start(); time.Sleep(time.Millisecond); return nil }
func CopyWithOption(to any, from any, opt Option) error { return Copy(to, from) }
GO
