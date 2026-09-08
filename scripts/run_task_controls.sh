#!/usr/bin/env bash
# Run the 7 non-hang controls for one task; print a one-line summary per control.
set -uo pipefail
T="$1"
cd /data/NL2RepoBench-integration-20260827
mkdir -p ".nl2repo/runs/${T}-controls"
for kind in empty stub forgery install-failure panic oversized-output background-process; do
  echo "=== [$T] CONTROL $kind"
  rm -rf "build/controls/${T}-${kind}"
  uv run nl2repo harbor prepare-control "catalog/tasks/${T}" "$kind" --output build/controls --toolchain toolchain.lock.toml >/dev/null 2>&1 || { echo "[$T] $kind prepare FAILED"; continue; }
  R=".nl2repo/runs/${T}-controls/${kind}"
  rm -rf "$R"; mkdir -p "$R"
  ( cd harbor-runner && env PYTHONPATH=../src timeout 1500 uv run --frozen python ../scripts/harbor_safe_entry.py run -p "../build/controls/${T}-${kind}" -a oracle --jobs-dir "../$R" --yes >/dev/null 2>&1 )
  g=$(find "$R" -name grading.json | head -1)
  if [ -n "$g" ]; then
    python3 -c "import json;d=json.load(open('$g'));c=d['counts'];print('[$T] %-18s valid=%-5s collected=%-3s reward=%s'%('$kind',d.get('valid'),c['collected'],d.get('reward')))"
  else
    echo "[$T] $kind (no grading)"
  fi
done
echo "=== [$T] ALL CONTROLS DONE"
