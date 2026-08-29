#!/usr/bin/env bash
set -euo pipefail
revision='1416438a14118949d05be634124ab5d1c94c1f99'
source_digest='8061a883f29af255e7b3ba4da8c8f2b61a16e767e2ab40557443ad24a295b71a'
tmp='/tmp/msal-oracle-source'
rm -rf "$tmp" /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
git init -q "$tmp"
git -C "$tmp" remote add origin https://github.com/AzureAD/microsoft-authentication-library-for-python
git -C "$tmp" fetch -q --depth 1 origin "$revision"
git -C "$tmp" checkout -q --detach FETCH_HEAD
test "$(git -C "$tmp" rev-parse HEAD)" = "$revision"
git -C "$tmp" archive --format=tar "$revision" -o /tmp/msal-source.tar
printf '%s  %s\n' "$source_digest" /tmp/msal-source.tar | sha256sum --check --strict
tar -xf /tmp/msal-source.tar -C /workspace
rm -rf "$tmp" /tmp/msal-source.tar
