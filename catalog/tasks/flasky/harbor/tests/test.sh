#!/usr/bin/env bash
set -uo pipefail

EXPECTED=34
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
      'd45d5ffc8e05844cf2cdefc3c44710f79bdce461b1a474db879599173c1f07e8' '/tmp/candidate/tests/test_api.py' \
      'f0c1ff49a91f2e677e421793fa0df86515e1905c56b65442183a5148cc8e7c1c' '/tmp/candidate/tests/test_basics.py' \
      '421fcbba7a1b8148f4cabf030298d3c2b9a4b5b1b18ad54463848d478bc383b3' '/tmp/candidate/tests/test_client.py' \
      '95be8206326b64e524bb6216e291ba7dc597e64b4d99a70478633f0f5d0cdd28' '/tmp/candidate/tests/test_selenium.py' \
      '7c0ead17f8b367e15be40b3cb9088c7d1fa196f870a4db572a4a31c2528ec76c' '/tmp/candidate/tests/test_user_model.py' \
    | sha256sum -c - \
    > /logs/verifier/test-integrity-stdout.txt \
    2> /logs/verifier/test-integrity-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --reason frozen-test-integrity-failed
    exit 0
fi

# Candidate source layouts supported by the public instruction precede any
# stale editable package left by the verifier image.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate/src', '/tmp/candidate']\n" \
    > "$SITEPKG/_candidate_override.pth"

# Keep the frozen test copy readable but not writable by the candidate.
chown -R candidate:candidate /tmp/candidate /logs/verifier
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
