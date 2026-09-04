#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/go.mod <<'EOF'
module github.com/orcaman/concurrent-map/v2
go 1.26.5
EOF
: > /workspace/go.sum
cat > /workspace/main.go <<'EOF'
package main
import "fmt"
func main() { for i:=0; i<1000000; i++ { fmt.Println("oversized") } }
EOF
