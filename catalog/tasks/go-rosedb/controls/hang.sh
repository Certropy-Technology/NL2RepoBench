#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "$0")/control-assets/stub.sh"
sed -i '/func Open/c\func Open(Options) (*DB,error) { time.Sleep(60*time.Second); return \&DB{},nil }' rosedb.go
