#!/usr/bin/env bash
set -uo pipefail

readonly EXPECTED=46
readonly EXPECTED_COLLECTED=46
readonly CANDIDATE_UID=10001

mkdir -p /logs/verifier
chmod 0700 /logs/verifier
rm -f /logs/verifier/*
rm -rf /tmp/candidate /tmp/pss-results
mkdir -p /tmp/pss-results
chmod 1733 /tmp/pss-results
: > /tmp/pss-results/junit.xml
chmod 0666 /tmp/pss-results/junit.xml

if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt \
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --expected-collected "$EXPECTED_COLLECTED" --reason artifact-copy-failed
    exit 0
fi

# Preserve the legacy editable-install command. The candidate owns only its
# copied workspace; verifier fixtures and grading files remain root-owned.
chown -R "$CANDIDATE_UID:$CANDIDATE_UID" /tmp/candidate
timeout --signal=TERM --kill-after=5s 90s \
    runuser -u candidate -- env \
        HOME=/home/candidate \
        SHELL=/bin/bash \
        sh -c 'cd /tmp/candidate && python -m pip install -e .' \
    > /logs/verifier/install-stdout.txt \
    2> /logs/verifier/install-stderr.txt
install_exit_code=$?
if [[ "$install_exit_code" -ne 0 ]]; then
    python /tests/grade.py --expected "$EXPECTED" --expected-collected "$EXPECTED_COLLECTED" --reason installation-failed
    exit 0
fi

# Override the stale editable package left in the legacy verifier image and
# make the candidate checkout the first import location.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate']\n" \
    > "$SITEPKG/pss-nl2repobench-candidate.pth"

# Candidate-authored tests are never scored. Replace them with the immutable
# fixture copied from the pinned verifier image.
rm -rf /tmp/candidate/test
cp -a /tests/fixture/test /tmp/candidate/test
if ! (cd /tmp/candidate/test && sha256sum -c /tests/fixture/test.sha256) \
    > /logs/verifier/test-integrity-stdout.txt \
    2> /logs/verifier/test-integrity-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --expected-collected "$EXPECTED_COLLECTED" --reason frozen-test-integrity-failed
    exit 0
fi

# Keep the frozen test tree readable but not writable by the candidate.
chown -R "$CANDIDATE_UID:$CANDIDATE_UID" /tmp/candidate
chown -R root:root /tmp/candidate/test
chmod -R a-w /tmp/candidate/test

timeout --signal=TERM --kill-after=5s 300s \
    runuser -u candidate -- env \
        HOME=/home/candidate \
        LANG=C.UTF-8 \
        LC_ALL=C.UTF-8 \
        PYTHONHASHSEED=0 \
        PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
        sh -c 'cd /tmp/candidate && python -m pytest --continue-on-collection-errors test --junitxml=/tmp/pss-results/junit.xml --tb=short' \
    > /logs/verifier/pytest-stdout.txt \
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

if [[ -f /tmp/pss-results/junit.xml && ! -L /tmp/pss-results/junit.xml ]]; then
    cp /tmp/pss-results/junit.xml /logs/verifier/junit.xml
fi

python /tests/grade.py \
    --expected "$EXPECTED" \
    --expected-collected "$EXPECTED_COLLECTED" \
    --junit /logs/verifier/junit.xml \
    --pytest-exit-code "$pytest_exit_code"
exit 0
