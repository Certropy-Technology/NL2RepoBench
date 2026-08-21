#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier
rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate > /logs/verifier/copy-stdout.txt 2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected 4 --reason artifact-copy-failed
    exit 0
fi

# Replace candidate-created tests with the frozen image fixture.
rm -rf /tmp/candidate/tests
mkdir -p /tmp/candidate
cp -a /tests/fixture/tests /tmp/candidate/tests

# Put candidate source paths ahead of any editable install left by the base image.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate/src', '/tmp/candidate']\n" > "$SITEPKG/_candidate_override.pth"

if ! timeout 180 python -m pip install --no-index --no-build-isolation -e /tmp/candidate \
    > /logs/verifier/install-stdout.txt 2> /logs/verifier/install-stderr.txt; then
    python /tests/grade.py --expected 4 --reason installation-failed
    exit 0
fi

chown -R candidate:candidate /tmp/candidate /logs/verifier
runuser -u candidate -- env HOME=/home/candidate \
    sh -c "cd /tmp/candidate && timeout 1500 python -m pytest --continue-on-collection-errors tests --junitxml=/logs/verifier/junit.xml --tb=short" \
    > /logs/verifier/pytest-stdout.txt 2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?
python /tests/grade.py --expected 4 --junit /logs/verifier/junit.xml --pytest-exit-code "$pytest_exit_code"
