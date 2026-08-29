#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "$0")/control-assets/stub.sh"
sed -i '/import "time"/c\import ("time"; "os"; "strings")' rosedb.go
sed -i '/func Open/c\func Open(Options) (*DB,error) { _,_ = os.Stdout.WriteString(strings.Repeat("x",400000)); return \&DB{},nil }' rosedb.go
