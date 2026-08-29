#!/usr/bin/env bash
set -euo pipefail

revision='e2073db14d28d1c3299649dd0c2dd4205b43ebfd'
upstream='https://github.com/kjd/idna'
expected='9f05c7eabad5785cddefcb84a85230194b42dccb20b349027135854db25161f8'
work='/tmp/idna-oracle-source'
rm -rf "$work"
git clone --no-checkout "$upstream" "$work"
test "$(git -C "$work" rev-parse --verify "$revision^{commit}")" = "$revision"
git -C "$work" archive --format=tar --prefix=idna/ "$revision" > /tmp/idna-source.tar
test "$(sha256sum /tmp/idna-source.tar | awk '{print $1}')" = "$expected"
rm -rf /workspace/*
tar -xf /tmp/idna-source.tar -C /workspace --strip-components=1
rm -f /tmp/idna-source.tar
