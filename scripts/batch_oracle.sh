#!/usr/bin/env bash
set -euo pipefail

TASK_LIST="${1:-migration_tasks.txt}"
OUTPUT_DIR="${2:-.nl2repo/runs/nl2repobench-harbor-pilot/oracle-$(date -u +%Y%m%dT%H%M%SZ)}"

mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "Batch Oracle Testing"
echo "========================================"

total=0
success=0
failed=0

while IFS= read -r task_id; do
    [[ -z "$task_id" ]] && continue
    [[ "$task_id" =~ ^# ]] && continue
    
    task_path="catalog/tasks/$task_id/harbor"
    if [[ ! -d "$task_path" ]]; then
        echo "⏭️  Skipping $task_id (not found)"
        continue
    fi
    
    total=$((total + 1))
    echo ""
    echo "[$total] Testing Oracle: $task_id"
    echo "----------------------------------------"
    
    result_dir="$OUTPUT_DIR/${task_id}-oracle"
    
    cd harbor-runner
    if timeout 600 env PYTHONPATH=../src uv run --frozen python ../scripts/harbor_safe_entry.py run \
        -p "../$task_path" \
        -a oracle \
        --jobs-dir "../$result_dir" 2>&1 | tee "../${task_id}-oracle.log" | tail -20; then
        
        # Check reward
        grading_file=$(find "../$result_dir" -name "grading.json" 2>/dev/null | head -1)
        if [[ -f "$grading_file" ]]; then
            reward=$(jq -r '.reward' "$grading_file")
            valid=$(jq -r '.valid // true' "$grading_file")
            reason=$(jq -r '.reason // ""' "$grading_file")
            echo "  📊 Reward: $reward (valid=$valid reason=$reason)"
            
            if [[ "$valid" == "true" ]] && (( $(echo "$reward > 0.8" | bc -l) )); then
                success=$((success + 1))
                echo "  ✅ Success (reward > 0.8)"
            else
                echo "  ⚠️  Low reward: $reward"
            fi
        fi
    else
        failed=$((failed + 1))
        echo "  ❌ Failed"
    fi
    # Always clean this exact jobs directory after timeout, API failure, or
    # normal completion; never perform a global Docker cleanup here.
    python ../scripts/cleanup_harbor_trials.py --jobs-dir "../$result_dir" || true
    cd ..
    
done < "$TASK_LIST"

echo ""
echo "========================================"
echo "Batch Oracle Testing Complete"
echo "========================================"
echo "Total: $total"
echo "Success (>0.8): $success"
echo "Low/Failed: $failed"
