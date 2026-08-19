#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier

rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate     > /logs/verifier/copy-stdout.txt 2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected 248 --reason artifact-copy-failed
    exit 0
fi

# Replace candidate-created tests with the frozen test paths.
rm -rf /tmp/candidate/cerberus/tests
mkdir -p /tmp/candidate/$(dirname cerberus/tests)
cp -a /tests/fixture/cerberus/tests /tmp/candidate/cerberus/tests
rm -rf /tmp/candidate/cerberus/benchmarks/test_overall_performance_1.py
mkdir -p /tmp/candidate/$(dirname cerberus/benchmarks/test_overall_performance_1.py)
cp -a /tests/fixture/cerberus/benchmarks/test_overall_performance_1.py /tmp/candidate/cerberus/benchmarks/test_overall_performance_1.py
rm -rf /tmp/candidate/cerberus/benchmarks/test_overall_performance_2.py
mkdir -p /tmp/candidate/$(dirname cerberus/benchmarks/test_overall_performance_2.py)
cp -a /tests/fixture/cerberus/benchmarks/test_overall_performance_2.py /tmp/candidate/cerberus/benchmarks/test_overall_performance_2.py

# Executable .pth lines run at interpreter start and put candidate code first.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate/src', '/tmp/candidate']
"     > "$SITEPKG/_candidate_override.pth"


chown -R candidate:candidate /tmp/candidate /logs/verifier
runuser -u candidate -- env HOME=/home/candidate     sh -c "cd /tmp/candidate && python -m pytest --continue-on-collection-errors cerberus/tests cerberus/benchmarks/test_overall_performance_1.py cerberus/benchmarks/test_overall_performance_2.py            --junitxml=/logs/verifier/junit.xml --tb=short"     > /logs/verifier/pytest-stdout.txt 2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py --expected 248     --junit /logs/verifier/junit.xml --pytest-exit-code "$pytest_exit_code"
