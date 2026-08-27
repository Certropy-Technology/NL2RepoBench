#!/usr/bin/env bash
set -euo pipefail

bridge="$1"
proxy="$2"

call() {
  printf '%s\n' "$1" | "$proxy" "$bridge"
}

expect_value() {
  local request="$1"
  local expected="$2"
  local actual
  actual="$(call "$request")"
  test "$actual" = "{\"value\":\"$expected\"}"
}

expect_error() {
  local request="$1"
  local actual
  actual="$(call "$request")"
  case "$actual" in
    '{"error_type":"CallFailed","message":'*'}') ;;
    *) return 1 ;;
  esac
}

canonical="550e8400-e29b-41d4-a716-446655440000"
expect_value '{"operation":"parse","args":["550e8400-e29b-41d4-a716-446655440000"]}' "$canonical"
expect_value '{"operation":"parse","args":["550E8400E29B41D4A716446655440000"]}' "$canonical"
expect_value '{"operation":"parse","args":["URN:UUID:550E8400-E29B-41D4-A716-446655440000"]}' "$canonical"
expect_value '{"operation":"parse","args":["{550e8400-e29b-41d4-a716-446655440000}"]}' "$canonical"
expect_value '{"operation":"parse","args":["00000000-0000-0000-0000-000000000000"]}' '00000000-0000-0000-0000-000000000000'

expect_error '{"operation":"parse","args":["12345"]}'
expect_error '{"operation":"parse","args":["g50e8400-e29b-41d4-a716-446655440000"]}'
expect_error '{"operation":"parse","args":["550e8400xe29b-41d4-a716-446655440000"]}'
expect_error '{"operation":"parse","args":["url:uuid:550e8400-e29b-41d4-a716-446655440000"]}'

printf '%s\n' '{"operation":"parse","status":"passed"}'
