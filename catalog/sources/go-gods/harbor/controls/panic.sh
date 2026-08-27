#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [[ -f "$script_dir/stub-packages.sh" ]]; then
    bash "$script_dir/stub-packages.sh"
else
    bash "$script_dir/../controls/stub-packages.sh"
fi
mkdir -p cmd/bridge
cat > cmd/bridge/panic.go <<'GO'
package main

func init() { panic("control panic") }
GO
