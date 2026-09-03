#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
bash "$script_dir/stub-packages.sh"
mkdir -p cmd/bridge
cat > cmd/bridge/panic.go <<'GO'
package main

func init() { panic("control panic") }
GO
