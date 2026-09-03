#!/usr/bin/env bash
set -euo pipefail

BRIDGE=${1:?bridge executable is required}
PROXY=${2:?bridge proxy is required}

# assert_case compares the full JSON response against the frozen expectation.
assert_case() {
    local name=$1 request=$2 expected=$3 actual
    actual="$(printf '%s\n' "$request" | "$PROXY" "$BRIDGE")"
    python3 - "$name" "$actual" "$expected" <<'PY'
import json
import sys

name, actual_text, expected_text = sys.argv[1:]
try:
    actual = json.loads(actual_text)
    expected = json.loads(expected_text)
except json.JSONDecodeError as exc:
    raise SystemExit(f"{name}: invalid JSON response: {exc}: {actual_text!r}")
if actual != expected:
    raise SystemExit(f"{name}: response mismatch\nactual={actual!r}\nexpected={expected!r}")
PY
}

# assert_error checks only the documented error_type and a non-empty message.
assert_error() {
    local name=$1 request=$2 error_type=$3 actual
    actual="$(printf '%s\n' "$request" | "$PROXY" "$BRIDGE")"
    python3 - "$name" "$actual" "$error_type" <<'PY'
import json
import sys

name, actual_text, error_type = sys.argv[1:]
try:
    actual = json.loads(actual_text)
except json.JSONDecodeError as exc:
    raise SystemExit(f"{name}: invalid JSON response: {exc}: {actual_text!r}")
if not isinstance(actual, dict):
    raise SystemExit(f"{name}: response is not an object: {actual!r}")
if actual.get("error_type") != error_type:
    raise SystemExit(f"{name}: expected error_type {error_type!r}, got {actual!r}")
if not isinstance(actual.get("message"), str) or not actual["message"]:
    raise SystemExit(f"{name}: expected a non-empty message, got {actual!r}")
if "value" in actual:
    raise SystemExit(f"{name}: error response must not carry a value: {actual!r}")
PY
}

# 1. Recursive equality over exported struct fields.
assert_case profile-default \
    '{"operation":"equal_profiles","args":[{"name":"api","labels":{"env":"prod"},"scores":[1,2]},{"name":"api","labels":{"env":"prod"},"scores":[1,2]},"default"]}' \
    '{"value":true}'
# 2. EquateEmpty equates nil and empty maps/slices of the same type.
assert_case profile-empty \
    '{"operation":"equal_profiles","args":[{"name":"api","labels":{},"scores":[]},{"name":"api","labels":null,"scores":null},"empty"]}' \
    '{"value":true}'
# 3. A differing map value is not equal without EquateEmpty.
assert_case profile-different \
    '{"operation":"equal_profiles","args":[{"name":"api","labels":{"env":"prod"},"scores":[1,2]},{"name":"api","labels":{"env":"stage"},"scores":[1,2]},"default"]}' \
    '{"value":false}'
# 4. EquateApprox relative fraction accepts 100/101 at fraction 0.01.
assert_case approx-within \
    '{"operation":"equal_floats","args":[[100,1],[101,1.0005],0.01,0]}' \
    '{"value":true}'
# 5. EquateApprox rejects 100/102 at fraction 0.01.
assert_case approx-outside \
    '{"operation":"equal_floats","args":[[100],[102],0.01,0]}' \
    '{"value":false}'
# 6. EquateNaNs treats NaN (JSON null) pairs as equal.
assert_case nan-equality \
    '{"operation":"equal_floats","args":[[null],[null],0,0]}' \
    '{"value":true}'
# 7. SortSlices compares slices independent of element order.
assert_case sorted-slices \
    '{"operation":"equal_strings_sorted","args":[["beta","alpha"],["alpha","beta"]]}' \
    '{"value":true}'
# 8. SortMaps compares maps independent of key order.
assert_case sorted-maps \
    '{"operation":"equal_maps_sorted","args":[{"b":2,"a":1},{"a":1,"b":2}]}' \
    '{"value":true}'
# 9. Diff of two differing maps is non-empty with removal and insertion markers.
assert_case diff-values \
    '{"operation":"diff_values","args":[{"name":"old","count":1},{"name":"new","count":2}]}' \
    '{"value":{"nonempty":true,"has_removed":true,"has_inserted":true}}'
# 10. Diff names the differing path: struct field names and map keys.
assert_case diff-profile-paths \
    '{"operation":"diff_profile_paths","args":[{"name":"api","labels":{"env":"prod"},"scores":[1,2]},{"name":"svc","labels":{"env":"stage"},"scores":[1,3]}]}' \
    '{"value":{"nonempty":true,"mentions_name":true,"mentions_map":true,"mentions_scores":true}}'
# 11. Equal values produce an empty Diff.
assert_case diff-profile-equal \
    '{"operation":"diff_profile_paths","args":[{"name":"api","labels":{"env":"prod"},"scores":[1,2]},{"name":"api","labels":{"env":"prod"},"scores":[1,2]}]}' \
    '{"value":{"nonempty":false,"mentions_name":false,"mentions_map":false,"mentions_scores":false}}'
# 12. AllowUnexported compares the unexported field of the given type.
assert_case allow-unexported-equal \
    '{"operation":"equal_exported","args":[{"visible":"same","private":7},{"visible":"same","private":7}]}' \
    '{"value":true}'
# 13. AllowUnexported reports a differing unexported field.
assert_case allow-unexported-different \
    '{"operation":"equal_exported","args":[{"visible":"same","private":7},{"visible":"same","private":8}]}' \
    '{"value":false}'
# 14. Exporter(true) lets Equal introspect unexported fields.
assert_case exporter-equal \
    '{"operation":"equal_exporter","args":[{"visible":"same","private":7},{"visible":"same","private":7}]}' \
    '{"value":true}'
# 15. Exporter(true) reports a differing unexported field.
assert_case exporter-different \
    '{"operation":"equal_exporter","args":[{"visible":"same","private":7},{"visible":"same","private":8}]}' \
    '{"value":false}'
# 16. An unfiltered Ignore option is a programming error and must panic.
assert_case ignore-unfiltered-panics \
    '{"operation":"equal_ignore_unfiltered","args":[1,2]}' \
    '{"value":{"panicked":true}}'
# 17. EquateComparable compares the given comparable type with ==.
assert_case equate-comparable-equal \
    '{"operation":"equal_comparable","args":[[1,2],[1,2]]}' \
    '{"value":true}'
# 18. EquateComparable reports a differing field of that type.
assert_case equate-comparable-different \
    '{"operation":"equal_comparable","args":[[1,2],[1,3]]}' \
    '{"value":false}'
# 19. FilterPath(...true) + Ignore makes every comparison equal.
assert_case filter-path-ignore \
    '{"operation":"equal_filter_path","args":[1,2,"ignore"]}' \
    '{"value":true}'
# 20. FilterPath(...false) + Ignore leaves the comparison alone.
assert_case filter-path-keep-different \
    '{"operation":"equal_filter_path","args":[1,2,"keep"]}' \
    '{"value":false}'
# 21. FilterPath(...false) still reports equal values as equal.
assert_case filter-path-keep-equal \
    '{"operation":"equal_filter_path","args":[2,2,"keep"]}' \
    '{"value":true}'
# 22. FilterValues selects the values a nested option applies to.
assert_case filter-values-ignore \
    '{"operation":"equal_filter_values","args":[["a","_"],["a","b"]]}' \
    '{"value":true}'
# 23. Values outside the FilterValues predicate are compared normally.
assert_case filter-values-compare \
    '{"operation":"equal_filter_values","args":[["a","c"],["a","b"]]}' \
    '{"value":false}'
# 24. Transformer maps string values before comparison.
assert_case transformer-lower-equal \
    '{"operation":"equal_transformer","args":["lower","Alpha","alpha"]}' \
    '{"value":true}'
# 25. A Transformer must not invent equality beyond its function.
assert_case transformer-lower-different \
    '{"operation":"equal_transformer","args":["lower","Alpha","beta"]}' \
    '{"value":false}'
# 26. Transformer may change the compared type ([]string to int).
assert_case transformer-length-equal \
    '{"operation":"equal_transformer","args":["length",["a","b"],["x","y"]]}' \
    '{"value":true}'
# 27. Different transformed values stay unequal.
assert_case transformer-length-different \
    '{"operation":"equal_transformer","args":["length",["a","b"],["x"]]}' \
    '{"value":false}'
# 28. Comparer defines equality for the matching type.
assert_case comparer-equal \
    '{"operation":"equal_comparer","args":[2,4]}' \
    '{"value":true}'
# 29. Comparer is not applied to unrelated differences.
assert_case comparer-different \
    '{"operation":"equal_comparer","args":[2,3]}' \
    '{"value":false}'
# 30. EquateErrors matches a wrapped error against its target.
assert_case errors-wrapped \
    '{"operation":"equal_errors","args":["boom","boom","wrapped"]}' \
    '{"value":true}'
# 31. EquateErrors does not equate unrelated error values.
assert_case errors-distinct \
    '{"operation":"equal_errors","args":["boom","bang","distinct"]}' \
    '{"value":false}'
# 32. EquateApproxTime accepts times inside the margin.
assert_case times-within \
    '{"operation":"equal_times","args":["2026-01-01T00:00:00Z","2026-01-01T00:00:01Z",2000000000]}' \
    '{"value":true}'
# 33. EquateApproxTime rejects times outside the margin.
assert_case times-outside \
    '{"operation":"equal_times","args":["2026-01-01T00:00:00Z","2026-01-01T00:00:01Z",500000000]}' \
    '{"value":false}'
# 34. EquateApprox rejects a negative fraction or margin by panicking.
assert_error approx-negative-fraction \
    '{"operation":"equal_floats","args":[[1],[1],-0.01,0]}' \
    'CallFailed'
# 35. EquateApproxTime rejects a negative margin by panicking.
assert_error times-negative-margin-option \
    '{"operation":"equal_times","args":["2026-01-01T00:00:00Z","2026-01-01T00:00:01Z",-5]}' \
    'CallFailed'
# 36-38. Structured errors: bad input and unknown operations never panic.
assert_error times-invalid-time \
    '{"operation":"equal_times","args":["not-a-time","2026-01-01T00:00:01Z",500000000]}' \
    'InvalidInput'
assert_error invalid-operation \
    '{"operation":"not-supported","args":[]}' \
    'InvalidInput'
assert_error invalid-arity \
    '{"operation":"equal_profiles","args":[{"name":"x"},{"name":"x"}]}' \
    'InvalidInput'

printf '%s\n' 'contract::public-api: 38 assertions passed'
