#!/usr/bin/env bash
set -uo pipefail

readonly EXPECTED_EFFECTIVE=2
readonly EXPECTED_COLLECTED=92
readonly CANDIDATE_UID=10001

mkdir -p /logs/verifier
chmod 0700 /logs/verifier
rm -rf \
    /tmp/candidate \
    /tmp/candidate-results \
    /tmp/candidate-venv \
    /tmp/candidate-pytest-cache

if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt \
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py \
        --expected-effective "$EXPECTED_EFFECTIVE" \
        --expected-collected "$EXPECTED_COLLECTED" \
        --reason artifact-copy-failed \
        --failure-class verifier
    exit 0
fi

# Candidate-authored tests never participate in grading.
rm -rf /tmp/candidate/tests

if ! python -m venv --system-site-packages /tmp/candidate-venv \
    > /logs/verifier/venv-stdout.txt \
    2> /logs/verifier/venv-stderr.txt; then
    python /tests/grade.py \
        --expected-effective "$EXPECTED_EFFECTIVE" \
        --expected-collected "$EXPECTED_COLLECTED" \
        --reason verifier-environment-failed \
        --failure-class verifier
    exit 0
fi

mkdir -p /tmp/candidate-results
chmod 1733 /tmp/candidate-results
# Keep the report inode verifier-owned so the candidate cannot replace it with
# a symlink or another file before the trusted grader reads it.
: > /tmp/candidate-results/junit.xml
chmod 0666 /tmp/candidate-results/junit.xml
chown -R "$CANDIDATE_UID:$CANDIDATE_UID" /tmp/candidate /tmp/candidate-venv

timeout --signal=TERM --kill-after=5s 60s \
    runuser -u candidate -- env \
        HOME=/home/candidate \
        PIP_DISABLE_PIP_VERSION_CHECK=1 \
        PIP_NO_INDEX=1 \
        /tmp/candidate-venv/bin/python -m pip install \
            --no-build-isolation \
            --no-deps \
            --no-index \
            -e /tmp/candidate \
    > /logs/verifier/install-stdout.txt \
    2> /logs/verifier/install-stderr.txt
install_exit_code=$?

if [[ "$install_exit_code" -ne 0 ]]; then
    python /tests/grade.py \
        --expected-effective "$EXPECTED_EFFECTIVE" \
        --expected-collected "$EXPECTED_COLLECTED" \
        --reason candidate-installation-failed \
        --failure-class model
    exit 0
fi

mkdir -p /tmp/candidate/tests
cp -a /tests/fixture/tests/test_pyperclip.py \
    /tmp/candidate/tests/test_pyperclip.py

# Freeze the source and hidden test tree after installation. The test process
# can read them but cannot replace the frozen test path.
chown -R root:root /tmp/candidate
chmod -R a-w /tmp/candidate

timeout --signal=TERM --kill-after=5s 120s \
    runuser -u candidate -- env \
        HOME=/home/candidate \
        PYTHONDONTWRITEBYTECODE=1 \
        PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
        /tmp/candidate-venv/bin/python -m pytest \
            --collect-only \
            --continue-on-collection-errors \
            -o cache_dir=/tmp/candidate-pytest-cache \
            /tmp/candidate/tests \
    > /logs/verifier/collection-stdout.txt \
    2> /logs/verifier/collection-stderr.txt
collection_exit_code=$?

timeout --signal=TERM --kill-after=5s 300s \
    runuser -u candidate -- env \
        HOME=/home/candidate \
        PYTHONDONTWRITEBYTECODE=1 \
        PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
        /tmp/candidate-venv/bin/python -m pytest \
            --continue-on-collection-errors \
            -o cache_dir=/tmp/candidate-pytest-cache \
            /tmp/candidate/tests \
            --junitxml=/tmp/candidate-results/junit.xml \
            --tb=short \
    > /logs/verifier/pytest-stdout.txt \
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

if [[ -f /tmp/candidate-results/junit.xml && ! -L /tmp/candidate-results/junit.xml ]]; then
    cp /tmp/candidate-results/junit.xml /logs/verifier/junit.xml
fi

python /tests/grade.py \
    --expected-effective "$EXPECTED_EFFECTIVE" \
    --expected-collected "$EXPECTED_COLLECTED" \
    --junit /logs/verifier/junit.xml \
    --collection-exit-code "$collection_exit_code" \
    --pytest-exit-code "$pytest_exit_code"
