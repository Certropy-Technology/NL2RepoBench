#!/usr/bin/env bash
# Run oracle for one task; print one-line summary.
set -uo pipefail
T="$1"
cd /data/NL2RepoBench-integration-20260827
R=".nl2repo/runs/${T}-oracle-g1"
rm -rf "$R"; mkdir -p "$R"
( cd harbor-runner && env PYTHONPATH=../src timeout 2400 uv run --frozen python ../scripts/harbor_safe_entry.py run -p "../catalog/tasks/${T}" -a oracle --jobs-dir "../$R" --yes > "../.nl2repo/runs/${T}-oracle-g1.log" 2>&1 )
g=$(find "$R" -name grading.json | head -1)
if [ -n "$g" ]; then
  python3 -c "import json;d=json.load(open('$g'));c=d['counts'];print('[$T] oracle valid=%-5s collected=%-3s passed=%-3s reward=%s reason=%s'%(d.get('valid'),c['collected'],c['passed'],d.get('reward'),d.get('failure_reason')))"
else
  echo "[$T] oracle (no grading)"
fi
