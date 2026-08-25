#!/usr/bin/env bash
set -euo pipefail
bridge="$1"
proxy="$2"
output="$(printf '%s\n' '{"operation":"parse","args":["550e8400-e29b-41d4-a716-446655440000"]}' | "$proxy" "$bridge")"
test "$output" = '{"value":"550e8400-e29b-41d4-a716-446655440000"}'
printf '{"operation":"parse","status":"passed"}\n'
