#!/usr/bin/env bash
set -uo pipefail

EXPECTED=81
FROZEN_TEST_SHA256="05bba4db69922fc2a9722451e668bb0bcc86d9a1b26550864abd7a631c46c66a"

mkdir -p /logs/verifier
rm -f /logs/verifier/reward.json /logs/verifier/grading.json
rm -rf /tmp/candidate

if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt \
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --reason artifact-copy-failed
    exit 0
fi

# The root-level path is part of the frozen legacy contract. Replace any file
# supplied by the candidate with the verifier-owned bytes.
rm -rf /tmp/candidate/test_schedule.py
cp -a /tests/fixture/test_schedule.py /tmp/candidate/test_schedule.py
if ! printf '%s  %s\n' "$FROZEN_TEST_SHA256" /tmp/candidate/test_schedule.py \
    | sha256sum -c - \
    > /logs/verifier/test-integrity-stdout.txt \
    2> /logs/verifier/test-integrity-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --reason frozen-test-integrity-failed
    exit 0
fi

# Candidate source layouts supported by the public instruction are placed
# before image site-packages. The verifier image supplies only dependencies.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate/src', '/tmp/candidate']\n" \
    > "$SITEPKG/_candidate_override.pth"

chown -R candidate:candidate /tmp/candidate /logs/verifier
runuser -u candidate -- env \
    HOME=/home/candidate \
    TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONHASHSEED=0 \
    sh -c "cd /tmp/candidate && python -m pytest --continue-on-collection-errors test_schedule.py --junitxml=/logs/verifier/junit.xml --tb=short" \
    > /logs/verifier/pytest-stdout.txt \
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py \
    --expected "$EXPECTED" \
    --junit /logs/verifier/junit.xml \
    --pytest-exit-code "$pytest_exit_code"
exit 0
