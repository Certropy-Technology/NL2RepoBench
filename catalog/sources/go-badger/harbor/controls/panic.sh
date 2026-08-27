#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "$0")/../controls/stub.sh"
sed -i 's/func Open(Options) (\*DB,error) { return &DB{},nil }/func Open(Options) (*DB,error) { panic("control panic") }/' badger.go
