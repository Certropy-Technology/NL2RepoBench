#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "$0")/control-assets/stub.sh"
sed -i '/func Open/c\func Open(Options) (*DB,error) { panic("controlled panic") }' rosedb.go
