#!/usr/bin/env bash
set -euo pipefail
REV=02f9c577bcd0ad9fedfb0fd5dc598d323f7984bf
EXPECTED_SHA=5f7359441c2f6c58f1ee04134963b6b4c333ed62e45fdd4cacbdad4f6225a967
EXPECTED_SIZE=1648640
work=/tmp/pyasn1-modules-oracle-source
rm -rf "$work" /tmp/pyasn1-modules-archive /tmp/pyasn1-modules-extracted
mkdir -p "$work" /tmp/pyasn1-modules-extracted
git -C "$work" init -q
git -C "$work" remote add origin https://github.com/pyasn1/pyasn1-modules.git
git -C "$work" fetch --depth 1 origin "$REV"
actual=$(git -C "$work" rev-parse FETCH_HEAD)
test "$actual" = "$REV"
git -C "$work" archive --format=tar --prefix=pyasn1-modules/ "$actual" > /tmp/pyasn1-modules-archive
test "$(sha256sum /tmp/pyasn1-modules-archive | cut -d' ' -f1)" = "$EXPECTED_SHA"
test "$(wc -c < /tmp/pyasn1-modules-archive)" -eq "$EXPECTED_SIZE"
tar -xf /tmp/pyasn1-modules-archive -C /tmp/pyasn1-modules-extracted
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cp -a /tmp/pyasn1-modules-extracted/pyasn1-modules/. /workspace/
