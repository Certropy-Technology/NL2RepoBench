#!/usr/bin/env bash
set -euo pipefail
bridge="$1"
proxy="$2"
output="$(printf '%s\n' '{"operation":"normalize","args":["  hello  "]}' | "$proxy" "$bridge")"
test "$output" = '{"value":"hello"}'
printf '{"operation":"normalize","status":"passed"}\n'
