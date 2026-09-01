#!/usr/bin/env bash
set -euo pipefail

bridge=${1:?bridge executable is required}
proxy=${2:?bridge proxy is required}

assert_case() {
    local name=$1 request=$2 expected=$3 actual
    actual="$(printf '%s\n' "$request" | timeout --foreground 8s "$proxy" "$bridge")"
    if (( ${#actual} > 1024 )); then
        printf '%s: response exceeds 1024 bytes\n' "$name" >&2
        exit 1
    fi
    if [[ "$actual" != "$expected" ]]; then
        printf '%s: response mismatch\nactual=%s\nexpected=%s\n' \
            "$name" "$actual" "$expected" >&2
        exit 1
    fi
}

assert_case \
    base64-encode \
    '{"operation":"base64_encode","args":["Go!"]}' \
    '{"value":"R28h"}'
assert_case \
    reverse \
    '{"operation":"reverse","args":["Go!"]}' \
    '{"value":"!oG"}'
assert_case \
    int-to-roman \
    '{"operation":"int_to_roman","args":[1984]}' \
    '{"value":"MCMLXXXIV"}'
assert_case \
    rgb-to-hex \
    '{"operation":"rgb_to_hex","args":[52,152,219]}' \
    '{"value":3447003}'

printf '{"operation":"public-api","status":"passed"}\n'
