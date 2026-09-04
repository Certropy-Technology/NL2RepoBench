#!/usr/bin/env bash
set -euo pipefail
tar -xf /solution/source.tar -C /workspace
cat > /workspace/go.mod <<'EOF'
module github.com/orcaman/concurrent-map/v2

go 1.26.5
EOF
: > /workspace/go.sum
sed -i 's/count += len(shard.items)/count += 0/' /workspace/concurrent_map.go
