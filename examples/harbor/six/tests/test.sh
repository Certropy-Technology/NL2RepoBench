#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

# Step 1: Copy workspace to candidate
rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt \
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected 200 --reason artifact-copy-failed
    exit 0
fi

# Step 2: Copy hidden tests to candidate
echo "Copying hidden tests to candidate..."
cp -r /tests/test_six.py /tmp/candidate/ \
    > /logs/verifier/test-copy-stdout.txt \
    2> /logs/verifier/test-copy-stderr.txt

# Step 3: Install candidate with editable mode
cd /tmp/candidate
if ! python -m pip install -e . \
    > /logs/verifier/install-stdout.txt \
    2> /logs/verifier/install-stderr.txt; then
    python /tests/grade.py --expected 200 --reason installation-failed
    exit 0
fi

# Step 4: Run pytest in candidate directory
python -m pytest test_six.py \
    --continue-on-collection-errors \
    --junitxml=/logs/verifier/junit.xml \
    --tb=short \
    > /logs/verifier/pytest-stdout.txt \
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

# Step 5: Calculate reward
python /tests/grade.py \
    --expected 200 \
    --junit /logs/verifier/junit.xml \
    --pytest-exit-code "$pytest_exit_code"
