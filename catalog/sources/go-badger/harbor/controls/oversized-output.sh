#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "$0")/../controls/stub.sh"
sed -i 's/import "errors"/import ("errors"; "fmt"; "strings")/' badger.go
sed -i 's/func Open(Options) (\*DB,error) { return &DB{},nil }/func Open(Options) (*DB,error) { fmt.Print(strings.Repeat("x", 2000000)); return \&DB{},nil }/' badger.go
