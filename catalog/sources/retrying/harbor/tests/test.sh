#!/usr/bin/env bash
set -uo pipefail

EXPECTED=23
mkdir -p /logs/verifier

rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt \
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --reason artifact-copy-failed
    exit 0
fi

# Replace candidate-created tests with the exact frozen legacy test path.
rm -f /tmp/candidate/test_retrying.py
cp -a /tests/fixture/test_retrying.py /tmp/candidate/test_retrying.py

# Install the candidate with the legacy editable-install contract. Runtime
# dependencies are already present in the pinned verifier image.
if ! python -m pip install --no-deps --no-build-isolation -e /tmp/candidate \
    > /logs/verifier/install-stdout.txt \
    2> /logs/verifier/install-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --reason installation-failed
    exit 0
fi

# Keep candidate imports ahead of any verifier-site packages.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate']\n" \
    > "$SITEPKG/_candidate_override.pth"

chown -R candidate:candidate /tmp/candidate /logs/verifier
runuser -u candidate -- env HOME=/home/candidate \
    sh -c "cd /tmp/candidate && python -m pytest --continue-on-collection-errors test_retrying.py \
           --junitxml=/logs/verifier/junit.xml --tb=short" \
    > /logs/verifier/pytest-stdout.txt \
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py --expected "$EXPECTED" \
    --junit /logs/verifier/junit.xml --pytest-exit-code "$pytest_exit_code"
