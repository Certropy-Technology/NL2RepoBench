#!/usr/bin/env bash
# Oracle reference solution for the frozen `records` task.
#
# The agent image runs with no network, and fetching upstream would also leak
# the reference implementation, so this script is purely local: the frozen
# source tree at revision 72efce67874d1b40ac2a35542127e8830da49707 travels
# inside the private Oracle bundle and is unpacked from /solution.
set -euo pipefail

SOURCE_ARCHIVE=/solution/source.tar
SOURCE_ARCHIVE_SHA256=a052449f71402b8e53d0121e08a79d2c6a10e65cbc43cdfdb715ff077a8b6e12

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
tar -xf "$SOURCE_ARCHIVE" -C /workspace

# The upstream test suite is deliberately absent: the hidden slice lives in the
# separate verifier image, and shipping tests here would leak the denominator.
test -f /workspace/records.py
test -f /workspace/setup.py
test -f /workspace/README.rst
test -f /workspace/HISTORY.rst
test ! -e /workspace/tests
