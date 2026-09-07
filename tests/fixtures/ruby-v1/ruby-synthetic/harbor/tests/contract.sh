#!/usr/bin/env bash
set -euo pipefail
proxy="$1"
bridge="$2"
candidate="$3"
bundle="$4"
output="$(printf '%s\n' '{"operation":"normalize","args":["  hello  "]}' | "$proxy" "$bridge" "$candidate" "$bundle")"
test "$output" = '{"value":"hello"}'
printf '{"operation":"normalize","status":"passed"}\n'
