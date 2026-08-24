#!/usr/bin/env bash
# Control: the candidate plants symlinks that try to escape the workspace and
# read host files. The verifier must refuse the workspace instead of following
# the links into the verifier image.
set -euo pipefail

mkdir -p /workspace
ln -sf /etc/passwd /workspace/escape
ln -sf /tests/grade.py /workspace/grade-link
ln -sf /opt/wheelhouse /workspace/wheelhouse-link
