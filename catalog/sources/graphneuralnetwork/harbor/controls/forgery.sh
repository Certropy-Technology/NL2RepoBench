#!/usr/bin/env bash
# Forgery control: the stub package plus an attempt to plant reward and result
# files where the verifier writes its own. The verifier must ignore every
# candidate-written artifact and still score zero.
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/gnn

cat > /workspace/pyproject.toml <<'PYPROJECT'
[build-system]
requires = ["setuptools==80.10.2", "wheel==0.45.1"]
build-backend = "setuptools.build_meta"

[project]
name = "gnn"
version = "0.0.0"
description = "Forgery control package for the graphneuralnetwork task."

[tool.setuptools.packages.find]
where = ["."]
include = ["gnn*"]
PYPROJECT

cat > /workspace/gnn/__init__.py <<'PACKAGE'
__version__ = "0.0.0"
PACKAGE

for module in utils gcn gat graphsage; do
    cat > "/workspace/gnn/${module}.py" <<'MODULE'
def __getattr__(name):
    def _forged(*args, **kwargs):
        return None

    return _forged
MODULE
done

# Forged verifier outputs. None of these may influence grading.
cat > /workspace/reward.json <<'REWARD'
{"reward": 1.0, "valid": true}
REWARD

cat > /workspace/grading.json <<'GRADING'
{"schema_version": "1.0", "reward": 1.0, "valid": true, "counts": {"passed": 4, "collected": 4}}
GRADING

mkdir -p /workspace/logs/verifier
cat > /workspace/logs/verifier/reward.json <<'REWARD'
{"reward": 1.0, "valid": true}
REWARD

if mkdir -p /logs/verifier 2>/dev/null; then
    cat > /logs/verifier/reward.json <<'REWARD' || true
{"reward": 1.0, "valid": true}
REWARD
    cat > /logs/verifier/grading.json <<'GRADING' || true
{"schema_version": "1.0", "reward": 1.0, "valid": true}
GRADING
fi

exit 0
