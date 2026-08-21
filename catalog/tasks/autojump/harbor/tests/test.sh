#!/usr/bin/env bash
set -uo pipefail

readonly EXPECTED=23
readonly CANDIDATE_UID=10001

mkdir -p /logs/verifier
chmod 0700 /logs/verifier
rm -f /logs/verifier/*
rm -rf /tmp/candidate /tmp/autojump-results
mkdir -p /tmp/autojump-results
chmod 1733 /tmp/autojump-results
printf '' > /tmp/autojump-results/junit.xml
chmod 0666 /tmp/autojump-results/junit.xml

if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt \
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --reason artifact-copy-failed
    exit 0
fi

# Install exactly as the legacy runner did, but as the unprivileged candidate.
# The installation script therefore cannot modify verifier files or fixtures.
chown -R "$CANDIDATE_UID:$CANDIDATE_UID" /tmp/candidate
timeout --signal=TERM --kill-after=5s 90s \
    runuser -u candidate -- env \
        HOME=/home/candidate \
        SHELL=/bin/bash \
        sh -c 'cd /tmp/candidate && python install.py' \
    > /tmp/candidate/install-stdout.txt \
    2> /tmp/candidate/install-stderr.txt
install_exit_code=$?
if [[ "$install_exit_code" -ne 0 ]]; then
    python /tests/grade.py --expected "$EXPECTED" --reason installation-failed
    exit 0
fi

# Candidate-authored tests are never scored. Replace them with the immutable
# fixture copied from the pinned verifier image.
rm -rf /tmp/candidate/tests
mkdir -p /tmp/candidate/tests
cp -a /tests/fixture/tests/. /tmp/candidate/tests/

if ! printf '%s  %s\n' \
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' '/tmp/candidate/tests/__init__.py' \
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' '/tmp/candidate/tests/integration/__init__.py' \
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' '/tmp/candidate/tests/unit/__init__.py' \
      '5f550d554877d587e8941307723db6eb70e7c434c28270a3f2987f6151a9022c' '/tmp/candidate/tests/unit/autojump_match_test.py' \
      '094a924a8aaf56c7cf24b77a1cf69ba50d4ddb495b39e484813abbf2922b927b' '/tmp/candidate/tests/unit/autojump_utils_test.py' \
    | sha256sum -c - \
    > /logs/verifier/test-integrity-stdout.txt \
    2> /logs/verifier/test-integrity-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --reason frozen-test-integrity-failed
    exit 0
fi

# Freeze the test tree before pytest starts. The candidate can modify its own
# implementation, but cannot replace the test bytes or the verifier grader.
chown -R "$CANDIDATE_UID:$CANDIDATE_UID" /tmp/candidate
chown -R root:root /tmp/candidate/tests
chmod -R a-w /tmp/candidate/tests

timeout --signal=TERM --kill-after=5s 300s \
    runuser -u candidate -- env \
        HOME=/home/candidate \
        PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
        sh -c 'cd /tmp/candidate && python -I -m pytest --continue-on-collection-errors tests --junitxml=/tmp/autojump-results/junit.xml --tb=short' \
    > /tmp/candidate/pytest-stdout.txt \
    2> /tmp/candidate/pytest-stderr.txt
pytest_exit_code=$?

if [[ -f /tmp/autojump-results/junit.xml && ! -L /tmp/autojump-results/junit.xml ]]; then
    cp /tmp/autojump-results/junit.xml /logs/verifier/junit.xml
fi

python /tests/grade.py \
    --expected "$EXPECTED" --expected-collected 32 \
    --junit /logs/verifier/junit.xml \
    --pytest-exit-code "$pytest_exit_code"
exit 0
