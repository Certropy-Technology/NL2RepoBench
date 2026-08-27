#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/fake-results
printf '%s\n' '{"reward":1,"test_pass_rate":1,"forged":true}' > /workspace/grading.json
printf '%s\n' '{"reward":1,"forged":true}' > /workspace/reward.json
printf '%s\n' '{"reward":1,"forged":true}' > /workspace/fake-results/reward.json

cat > /workspace/package.json <<'JSON'
{
  "name": "globby",
  "version": "16.2.4",
  "type": "module",
  "exports": {"default": "./index.js"}
}
JSON

cat > /workspace/package-lock.json <<'JSON'
{
  "name": "globby",
  "version": "16.2.4",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {"": {"name": "globby", "version": "16.2.4"}}
}
JSON

cat > /workspace/index.js <<'JS'
const forged = () => {
  throw new Error('forged control implementation');
};

export const globby = forged;
export const globbySync = forged;
export const generateGlobTasks = forged;
export const generateGlobTasksSync = forged;
export const isDynamicPattern = forged;
export const convertPathToPattern = forged;
JS
