#!/usr/bin/env bash
set -uo pipefail

LOG_DIR=/logs/verifier
EXPECTED=11
mkdir -p "$LOG_DIR"
chmod 0700 "$LOG_DIR"
rm -f "$LOG_DIR/reward.json" "$LOG_DIR/grading.json"

write_failure() {
    local reason=$1
    local failure_class=$2
    python /tests/grade.py \
        --expected "$EXPECTED" \
        --reason "$reason" \
        --failure-class "$failure_class"
}

if ! sha256sum --check --strict /tests/fixture-manifest.sha256 \
    > "$LOG_DIR/fixture-integrity-stdout.txt" \
    2> "$LOG_DIR/fixture-integrity-stderr.txt"; then
    write_failure verifier-fixture-integrity-failed verifier
    exit 0
fi

rm -rf /tmp/candidate /tmp/test-workdir /tmp/candidate-results
if ! cp -a /workspace /tmp/candidate \
    > "$LOG_DIR/copy-stdout.txt" \
    2> "$LOG_DIR/copy-stderr.txt"; then
    write_failure artifact-copy-failed verifier
    exit 0
fi

rm -rf /tmp/candidate/.git /tmp/candidate/tests
mkdir -p /tmp/test-workdir /tmp/candidate-results
chown -R candidate:candidate \
    /tmp/candidate \
    /tmp/test-workdir \
    /tmp/candidate-results \
    /home/candidate

if ! runuser -u candidate -- env HOME=/home/candidate \
    sh -c 'cd /tmp/test-workdir \
        && git init --quiet \
        && git config user.name "NL2RepoBench Verifier" \
        && git config user.email "verifier@invalid.example" \
        && git commit --quiet --allow-empty -m baseline' \
    > "$LOG_DIR/git-setup-stdout.txt" \
    2> "$LOG_DIR/git-setup-stderr.txt"; then
    write_failure verifier-git-fixture-failed verifier
    exit 0
fi

if ! runuser -u candidate -- env HOME=/home/candidate \
    python -m pip install \
        --disable-pip-version-check \
        --no-deps \
        --no-build-isolation \
        --user \
        --editable /tmp/candidate \
    > "$LOG_DIR/install-stdout.txt" \
    2> "$LOG_DIR/install-stderr.txt"; then
    write_failure candidate-installation-failed model
    exit 0
fi

chown -R root:root /tmp/candidate
find /tmp/candidate -type d -exec chmod go-w '{}' +
find /tmp/candidate -type f -exec chmod go-w '{}' +

runuser -u candidate -- env \
    HOME=/home/candidate \
    PYTHONPATH=/tmp/candidate \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
    sh -c 'cd /tmp/test-workdir \
        && python -m pytest \
            --continue-on-collection-errors \
            /tests/fixture/tests \
            --junitxml=/tmp/candidate-results/junit.xml \
            --tb=short' \
    > "$LOG_DIR/pytest-stdout.txt" \
    2> "$LOG_DIR/pytest-stderr.txt"
pytest_exit_code=$?

pkill -KILL -u candidate 2>/dev/null || true

if ! sha256sum --check --strict /tests/fixture-manifest.sha256 \
    > "$LOG_DIR/fixture-integrity-after-stdout.txt" \
    2> "$LOG_DIR/fixture-integrity-after-stderr.txt"; then
    write_failure verifier-fixture-integrity-failed verifier
    exit 0
fi

python /tests/grade.py \
    --expected "$EXPECTED" \
    --junit /tmp/candidate-results/junit.xml \
    --pytest-exit-code "$pytest_exit_code"
