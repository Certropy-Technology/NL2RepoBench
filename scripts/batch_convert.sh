#!/usr/bin/env bash
set -euo pipefail

TASK_LIST="${1:-batch_tasks.txt}"
OUTPUT_DIR="${2:-catalog/sources}"

if [[ ! -f "$TASK_LIST" ]]; then
    echo "❌ Task list not found: $TASK_LIST"
    exit 1
fi

echo "========================================"
echo "Batch Converting Tasks"
echo "========================================"
echo "Task list: $TASK_LIST"
echo "Output dir: $OUTPUT_DIR"
echo ""

total=$(wc -l < "$TASK_LIST")
current=0
success=0
failed=0

while IFS= read -r task_id; do
    # Skip empty lines and comments
    [[ -z "$task_id" ]] && continue
    [[ "$task_id" =~ ^# ]] && continue
    
    current=$((current + 1))
    echo ""
    echo "[$current/$total] Converting: $task_id"
    echo "----------------------------------------"
    
    # Try to find upstream URL from known repositories
    upstream_url=""
    case "$task_id" in
        aiofiles) upstream_url="https://github.com/Tinche/aiofiles" ;;
        boltons) upstream_url="https://github.com/mahmoud/boltons" ;;
        cerberus) upstream_url="https://github.com/pyeve/cerberus" ;;
        decouple) upstream_url="https://github.com/HBNetwork/python-decouple" ;;
        ftfy) upstream_url="https://github.com/rspeer/python-ftfy" ;;
        humanize) upstream_url="https://github.com/python-humanize/humanize" ;;
        parse) upstream_url="https://github.com/r1chardj0n3s/parse" ;;
        pluggy) upstream_url="https://github.com/pytest-dev/pluggy" ;;
        pytz) upstream_url="https://github.com/stub42/pytz" ;;
        six) upstream_url="https://github.com/benjaminp/six" ;;
        tabulate) upstream_url="https://github.com/astanin/python-tabulate" ;;
        arguably) upstream_url="https://github.com/treykeown/arguably" ;;
        *) 
            echo "  ⚠️  Unknown task, will need manual upstream URL"
            ;;
    esac
    
    # Run conversion
    if [[ -n "$upstream_url" ]]; then
        if python scripts/convert_testfiles_to_harbor.py "$task_id" \
            --upstream-url "$upstream_url" \
            --output "$OUTPUT_DIR" 2>&1 | tee "/tmp/convert_${task_id}.log"; then
            
            # Get upstream tests
            echo ""
            echo "  📥 Fetching upstream tests..."
            tmp_dir="/tmp/${task_id}-upstream"
            rm -rf "$tmp_dir"
            
            if git clone --depth 1 "$upstream_url" "$tmp_dir" 2>/dev/null; then
                mkdir -p "$OUTPUT_DIR/$task_id/harbor/tests/fixture"
                while IFS= read -r rel; do
                    [[ -z "$rel" ]] && continue
                    if [[ ! -e "$tmp_dir/$rel" ]]; then
                        echo "  ⚠️  Upstream path missing: $rel"
                        continue
                    fi
                    mkdir -p "$OUTPUT_DIR/$task_id/harbor/tests/fixture/$(dirname "$rel")"
                    cp -a "$tmp_dir/$rel" "$OUTPUT_DIR/$task_id/harbor/tests/fixture/$rel"
                    echo "  ✓ Copied $rel"
                done < <(python3 - "$task_id" <<'PY'
import json
import sys
from pathlib import Path

task = Path("test_files") / sys.argv[1]
for path in json.loads((task / "test_files.json").read_text()):
    print(path)
PY
                )
            else
                echo "  ⚠️  Failed to clone upstream, will need manual test copy"
            fi
            
            success=$((success + 1))
            echo "  ✅ Success"
        else
            failed=$((failed + 1))
            echo "  ❌ Failed (see /tmp/convert_${task_id}.log)"
        fi
    else
        echo "  ⏭️  Skipping (no upstream URL)"
    fi
    
done < "$TASK_LIST"

echo ""
echo "========================================"
echo "Batch Conversion Complete"
echo "========================================"
echo "Total: $total"
echo "Success: $success"
echo "Failed: $failed"
echo "Skipped: $((total - success - failed))"
echo ""
echo "Next steps:"
echo "1. Review generated tasks in $OUTPUT_DIR"
echo "2. Manually fix any failed conversions"
echo "3. Run Oracle tests: bash scripts/batch_oracle.sh"
