#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "$0")/../controls/stub.sh"
sed -i 's/import "errors"/import ("errors"; "time")/' badger.go
sed -i 's/func Open(Options) (\*DB,error) { return &DB{},nil }/func Open(Options) (*DB,error) { time.Sleep(60*time.Second); return \&DB{},nil }/' badger.go
