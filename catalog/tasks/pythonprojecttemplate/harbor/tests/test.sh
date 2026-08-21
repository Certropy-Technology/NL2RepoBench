#!/usr/bin/env bash
set -uo pipefail

EXPECTED=36
mkdir -p /logs/verifier

rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt \
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --reason artifact-copy-failed
    exit 0
fi

# Replace candidate-created tests with the immutable fixture copied from the
# pinned legacy image. No test bytes are stored in the catalog task.
rm -rf /tmp/candidate/tests
mkdir -p /tmp/candidate
cp -a /tests/fixture/tests /tmp/candidate/tests

# Keep candidate imports ahead of the preinstalled Oracle package. The image
# supplies numpy and pytest, so this verifier remains offline at runtime.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate/src', '/tmp/candidate']\n" \
    > "$SITEPKG/_candidate_override.pth"

chown -R candidate:candidate /tmp/candidate /logs/verifier
runuser -u candidate -- env HOME=/home/candidate \
    sh -c "cd /tmp/candidate && python -m pytest --continue-on-collection-errors tests \
           --junitxml=/logs/verifier/junit.xml --tb=short" \
    > /logs/verifier/pytest-stdout.txt \
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py --expected "$EXPECTED" \
    --junit /logs/verifier/junit.xml --pytest-exit-code "$pytest_exit_code"
