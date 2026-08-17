#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt \
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected 18 --reason artifact-copy-failed
    exit 0
fi

if ! python -m pip install --no-deps --no-build-isolation /tmp/candidate \
    > /logs/verifier/install-stdout.txt \
    2> /logs/verifier/install-stderr.txt; then
    python /tests/grade.py --expected 18 --reason installation-failed
    exit 0
fi

python -m pytest \
    --continue-on-collection-errors \
    --junitxml=/logs/verifier/junit.xml \
    /tests/test_ministats.py \
    > /logs/verifier/pytest-stdout.txt \
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py \
    --expected 18 \
    --junit /logs/verifier/junit.xml \
    --pytest-exit-code "$pytest_exit_code"
