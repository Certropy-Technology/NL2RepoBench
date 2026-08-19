#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier

rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate     > /logs/verifier/copy-stdout.txt 2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected 607 --reason artifact-copy-failed
    exit 0
fi

# Replace candidate-created tests with the frozen test paths.
rm -rf /tmp/candidate/tests/test_filesize.py
mkdir -p /tmp/candidate/$(dirname tests/test_filesize.py)
cp -a /tests/fixture/tests/test_filesize.py /tmp/candidate/tests/test_filesize.py
rm -rf /tmp/candidate/tests/test_i18n.py
mkdir -p /tmp/candidate/$(dirname tests/test_i18n.py)
cp -a /tests/fixture/tests/test_i18n.py /tmp/candidate/tests/test_i18n.py
rm -rf /tmp/candidate/tests/test_lists.py
mkdir -p /tmp/candidate/$(dirname tests/test_lists.py)
cp -a /tests/fixture/tests/test_lists.py /tmp/candidate/tests/test_lists.py
rm -rf /tmp/candidate/tests/test_number.py
mkdir -p /tmp/candidate/$(dirname tests/test_number.py)
cp -a /tests/fixture/tests/test_number.py /tmp/candidate/tests/test_number.py
rm -rf /tmp/candidate/tests/test_time.py
mkdir -p /tmp/candidate/$(dirname tests/test_time.py)
cp -a /tests/fixture/tests/test_time.py /tmp/candidate/tests/test_time.py

# Executable .pth lines run at interpreter start and put candidate code first.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate/src', '/tmp/candidate']
"     > "$SITEPKG/_candidate_override.pth"
mkdir -p /tmp/candidate/src/humanize
test -f /tmp/candidate/src/humanize/_version.py || echo '__version__ = "0.0.0"' > /tmp/candidate/src/humanize/_version.py

chown -R candidate:candidate /tmp/candidate /logs/verifier
runuser -u candidate -- env HOME=/home/candidate     sh -c "cd /tmp/candidate && python -m pytest --continue-on-collection-errors tests/test_filesize.py tests/test_i18n.py tests/test_lists.py tests/test_number.py tests/test_time.py            --junitxml=/logs/verifier/junit.xml --tb=short"     > /logs/verifier/pytest-stdout.txt 2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py --expected 607     --junit /logs/verifier/junit.xml --pytest-exit-code "$pytest_exit_code"
