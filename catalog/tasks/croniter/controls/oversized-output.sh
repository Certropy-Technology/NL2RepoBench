#!/bin/bash
# Oversized output control - generates large stdout
echo "[CONTROL:OVERSIZED] Generating large output"

# Create valid stub first
bash "$(dirname "$0")/stub.sh"

# Generate large output
for i in {1..10000}; do
    echo "Line $i: $(printf 'X%.0s' {1..100})"
done

echo "[CONTROL:OVERSIZED] Output generation complete"
