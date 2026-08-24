#!/usr/bin/env bash
set -uo pipefail

readonly EXPECTED=217
readonly EXPECTED_COLLECTED=217
readonly EXPECTED_SKIPPED=0
readonly CANDIDATE_UID=10001
readonly INSTALL_TIMEOUT=120s
readonly TEST_TIMEOUT=600s

mkdir -p /logs/verifier
chmod 0700 /logs/verifier
rm -f /logs/verifier/*
rm -rf /tmp/candidate /tmp/pandarallel-results /tmp/pandarallel-tmp
mkdir -p /tmp/pandarallel-results /tmp/pandarallel-tmp
chmod 1733 /tmp/pandarallel-results /tmp/pandarallel-tmp
: > /tmp/pandarallel-results/junit.xml
chmod 0666 /tmp/pandarallel-results/junit.xml

if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt \
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --expected-collected "$EXPECTED_COLLECTED" \
        --expected-skipped "$EXPECTED_SKIPPED" --reason artifact-copy-failed
    exit 0
fi

# Install the candidate as an unprivileged user. The verifier image already
# contains the pinned runtime dependencies, so resolution is deliberately
# offline and dependency installation is not allowed to reach an index.
chown -R "$CANDIDATE_UID:$CANDIDATE_UID" /tmp/candidate /tmp/pandarallel-tmp
timeout --signal=TERM --kill-after=10s "$INSTALL_TIMEOUT" \
    runuser -u candidate -- env \
        HOME=/home/candidate \
        LANG=C.UTF-8 \
        LC_ALL=C.UTF-8 \
        PIP_DISABLE_PIP_VERSION_CHECK=1 \
        sh -c 'cd /tmp/candidate && python -m pip install --user --no-deps --no-build-isolation -e .' \
    > /logs/verifier/install-stdout.txt \
    2> /logs/verifier/install-stderr.txt
install_exit_code=$?
if [[ "$install_exit_code" -ne 0 ]]; then
    python /tests/grade.py --expected "$EXPECTED" --expected-collected "$EXPECTED_COLLECTED" \
        --expected-skipped "$EXPECTED_SKIPPED" --reason installation-failed
    exit 0
fi

# Candidate-authored tests are never scored. Replace them with the immutable
# fixture copied from the pinned verifier image.
rm -rf /tmp/candidate/tests
mkdir -p /tmp/candidate/tests
cp -a /tests/fixture/tests/. /tmp/candidate/tests/

if ! printf '%s  %s\n' \
      '94c75928f37417101654b14bd9598951e82c462fb0120b040c804229aaacbbe5' '/tmp/candidate/tests/test_pandarallel.py' \
    | sha256sum -c - \
    > /logs/verifier/test-integrity-stdout.txt \
    2> /logs/verifier/test-integrity-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --expected-collected "$EXPECTED_COLLECTED" \
        --expected-skipped "$EXPECTED_SKIPPED" --reason frozen-test-integrity-failed
    exit 0
fi

# Freeze the hidden test bytes and candidate workspace before starting the
# test process. The implementation is read-only during grading; its temporary
# files and JUnit report live outside this tree.
chown -R root:root /tmp/candidate
chmod -R a+rX /tmp/candidate
chmod -R a-w /tmp/candidate

# Limit native math-library fan-out: the task itself creates two Python worker
# processes, and unconstrained BLAS threads would make the small tests flaky.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export BLIS_NUM_THREADS=1

# Run the frozen tests as an unprivileged candidate. The result file is a
# root-created regular file in a sticky directory, so the candidate cannot
# replace it with a symlink or redirect the trusted grader's output.
timeout --signal=TERM --kill-after=10s "$TEST_TIMEOUT" \
    runuser -u candidate -- env \
        HOME=/home/candidate \
        LANG=C.UTF-8 \
        LC_ALL=C.UTF-8 \
        PYTHONDONTWRITEBYTECODE=1 \
        PYTHONHASHSEED=0 \
        PYTHONNOUSERSITE=1 \
        PYTHONPATH=/tmp/candidate \
        PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
        TMPDIR=/tmp/pandarallel-tmp \
        sh -c 'cd /tmp/candidate && python -s -m pytest -p no:cacheprovider --basetemp=/tmp/pandarallel-tmp/pytest --continue-on-collection-errors tests --junitxml=/tmp/pandarallel-results/junit.xml --tb=short' \
    > /logs/verifier/pytest-stdout.txt \
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

if [[ -f /tmp/pandarallel-results/junit.xml && ! -L /tmp/pandarallel-results/junit.xml ]]; then
    cp /tmp/pandarallel-results/junit.xml /logs/verifier/junit.xml
fi

python /tests/grade.py \
    --expected "$EXPECTED" \
    --expected-collected "$EXPECTED_COLLECTED" \
    --expected-skipped "$EXPECTED_SKIPPED" \
    --junit /logs/verifier/junit.xml \
    --pytest-exit-code "$pytest_exit_code"
exit 0
