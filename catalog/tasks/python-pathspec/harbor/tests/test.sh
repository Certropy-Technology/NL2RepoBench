#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier

rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate     > /logs/verifier/copy-stdout.txt 2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected 119 --reason artifact-copy-failed
    exit 0
fi

# Replace candidate-created tests with the frozen test paths.
rm -rf /tmp/candidate/tests/test_01_util.py
mkdir -p /tmp/candidate/$(dirname tests/test_01_util.py)
cp -a /tests/fixture/tests/test_01_util.py /tmp/candidate/tests/test_01_util.py
rm -rf /tmp/candidate/tests/test_02_gitwildmatch.py
mkdir -p /tmp/candidate/$(dirname tests/test_02_gitwildmatch.py)
cp -a /tests/fixture/tests/test_02_gitwildmatch.py /tmp/candidate/tests/test_02_gitwildmatch.py
rm -rf /tmp/candidate/tests/test_03_pathspec.py
mkdir -p /tmp/candidate/$(dirname tests/test_03_pathspec.py)
cp -a /tests/fixture/tests/test_03_pathspec.py /tmp/candidate/tests/test_03_pathspec.py
rm -rf /tmp/candidate/tests/test_04_gitignore.py
mkdir -p /tmp/candidate/$(dirname tests/test_04_gitignore.py)
cp -a /tests/fixture/tests/test_04_gitignore.py /tmp/candidate/tests/test_04_gitignore.py

# Executable .pth lines run at interpreter start and put candidate code first.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate/src', '/tmp/candidate']
"     > "$SITEPKG/_candidate_override.pth"


chown -R candidate:candidate /tmp/candidate /logs/verifier
runuser -u candidate -- env HOME=/home/candidate     sh -c "cd /tmp/candidate && python -m pytest --continue-on-collection-errors tests/test_01_util.py tests/test_02_gitwildmatch.py tests/test_03_pathspec.py tests/test_04_gitignore.py            --junitxml=/logs/verifier/junit.xml --tb=short"     > /logs/verifier/pytest-stdout.txt 2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py --expected 119     --junit /logs/verifier/junit.xml --pytest-exit-code "$pytest_exit_code"
