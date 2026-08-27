#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "$0")/../controls/stub.sh"
sed -i 's/import "errors"/import ("errors"; "os\/exec")/' badger.go
sed -i 's/func Open(Options) (\*DB,error) { return &DB{},nil }/func Open(Options) (*DB,error) { _ = exec.Command("sh", "-c", "sleep 60").Start(); return \&DB{},nil }/' badger.go
