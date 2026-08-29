#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "$0")/control-assets/stub.sh"
sed -i '/import "time"/c\import ("time"; "os/exec")' rosedb.go
sed -i '/func Open/c\func Open(Options) (*DB,error) { _ = exec.Command("sh","-c","sleep 60").Start(); return \&DB{},nil }' rosedb.go
