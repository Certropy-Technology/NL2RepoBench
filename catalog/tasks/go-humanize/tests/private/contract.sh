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
  test "$(call "$request")" = "{\"value\":\"$expected\"}"
}

expect_error() {
  local request="$1"
  case "$(call "$request")" in
    '{"error_type":"InvalidInput","message":'*'}') ;;
    *) return 1 ;;
  esac
}

expect_value '{"operation":"bytes","args":[0]}' '0 B'
expect_value '{"operation":"bytes","args":[82854982]}' '83 MB'
expect_value '{"operation":"bytes","args":[1000000000]}' '1.0 GB'
expect_value '{"operation":"ibytes","args":[82854982]}' '79 MiB'
expect_value '{"operation":"ibytes","args":[1024]}' '1.0 KiB'
expect_value '{"operation":"comma","args":[834142]}' '834,142'
expect_value '{"operation":"comma","args":[-9223372036854775808]}' '-9,223,372,036,854,775,808'
expect_value '{"operation":"comma","args":[0]}' '0'
expect_value '{"operation":"ftoa","args":[12.340000]}' '12.34'
expect_value '{"operation":"ftoa","args":[1.23456789]}' '1.234568'
expect_value '{"operation":"ftoa_with_digits","args":[12.34567,2]}' '12.34'
expect_value '{"operation":"ftoa_with_digits","args":[12.30000,0]}' '12'
expect_value '{"operation":"ordinal","args":[1]}' '1st'
expect_value '{"operation":"ordinal","args":[12]}' '12th'
expect_value '{"operation":"ordinal","args":[23]}' '23rd'
expect_value '{"operation":"ordinal","args":[-2]}' '-2th'
expect_value '{"operation":"si","args":[1000000,"B"]}' '1 MB'
expect_value '{"operation":"si","args":[-0.0025,"A"]}' '-2.5 mA'
expect_value '{"operation":"si_with_digits","args":[2.2345e-12,2,"F"]}' '2.23 pF'
expect_value '{"operation":"si_with_digits","args":[0,3,"V"]}' '0 V'
expect_value '{"operation":"plural_word","args":[1,"cat",""]}' 'cat'
expect_value '{"operation":"plural_word","args":[2,"cat",""]}' 'cats'
expect_value '{"operation":"plural_word","args":[2,"index",""]}' 'indices'
expect_value '{"operation":"plural_word","args":[2,"city",""]}' 'cities'
expect_value '{"operation":"plural_word","args":[2,"box",""]}' 'boxes'
expect_value '{"operation":"plural_word","args":[2,"child","children"]}' 'children'
expect_value '{"operation":"plural","args":[1234,"item",""]}' '1,234 items'
expect_value '{"operation":"plural","args":[1,"item","items"]}' '1 item'
expect_error '{"operation":"bytes"}'
expect_error '{"operation":"comma","args":["not-an-int"]}'
expect_error '{"operation":"unknown","args":[]}'

printf '%s\n' '{"operation":"contract","status":"passed"}'
