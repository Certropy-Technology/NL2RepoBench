#!/usr/bin/env bash
set -uo pipefail

EXPECTED=31
mkdir -p /logs/verifier
rm -f /logs/verifier/reward.json /logs/verifier/grading.json
rm -rf /tmp/candidate

if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt \
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --reason artifact-copy-failed
    exit 0
fi

# The legacy contract selects the tests directory. Replace candidate-created
# tests with the verifier image's immutable fixture.
rm -rf /tmp/candidate/tests
mkdir -p /tmp/candidate/tests
cp -a /tests/fixture/tests/. /tmp/candidate/tests/

if ! printf '%s  %s\n' \
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' '/tmp/candidate/tests/__init__.py' \
      'ee39073d4f9fd5e91bf740bf227096abf0d8212a12f9c9000ae398ae4636c93c' '/tmp/candidate/tests/conftest.py' \
      '84558af919e0ff2256adfb026cbda8399a86f58a9c1cce51dca074fde3364073' '/tmp/candidate/tests/test_105.py' \
      '58d9ba8a6b4358ece2e11b61bb70d8e14ffddbc08e2d1df1163d15ce7bc6396d' '/tmp/candidate/tests/test_69.py' \
      'adaf50f977a0d0a7574995e58d75dad3935b99e4e6f696f479bda7b90aae9587' '/tmp/candidate/tests/test_records.py' \
      'f830d4b33e36a27ed0930af28259f6f6064cd154489e64cea8fa47f7d8d2f759' '/tmp/candidate/tests/test_transactions.py' \
    | sha256sum -c - \
    > /logs/verifier/test-integrity-stdout.txt \
    2> /logs/verifier/test-integrity-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --reason frozen-test-integrity-failed
    exit 0
fi

# Preserve the legacy editable-install step without resolving dependencies.
if ! python -m pip install --no-deps --no-build-isolation -e /tmp/candidate \
    > /logs/verifier/install-stdout.txt \
    2> /logs/verifier/install-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --reason installation-failed
    exit 0
fi

# Candidate source layouts supported by the public instruction precede any
# stale editable package left by the verifier image.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate/src', '/tmp/candidate']\n" \
    > "$SITEPKG/_candidate_override.pth"

# Keep the frozen test copy readable but not writable by the candidate.
chown -R candidate:candidate /tmp/candidate
chown -R root:root /tmp/candidate/tests
chmod -R a-w /tmp/candidate/tests

runuser -u candidate -- env \
    HOME=/home/candidate \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONHASHSEED=0 \
    sh -c "cd /tmp/candidate && python -m pytest --continue-on-collection-errors tests --junitxml=/tmp/candidate/junit.xml --tb=short" \
    > /logs/verifier/pytest-stdout.txt \
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py \
    --expected "$EXPECTED" \
    --junit /tmp/candidate/junit.xml \
    --pytest-exit-code "$pytest_exit_code"
exit 0
