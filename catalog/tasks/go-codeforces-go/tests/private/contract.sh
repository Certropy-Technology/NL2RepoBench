#!/usr/bin/env bash
set -euo pipefail

bridge="$1"
proxy="$2"

call() {
  printf '%s\n' "$1" | "$proxy" "$bridge"
}

snapshot() {
  python3 - "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" <<'PY'
import json
import sys

actual = json.loads(sys.argv[1])
assert set(actual) == {"value"}, actual
value = actual["value"]
expected_bits = json.loads(sys.argv[2])
assert value["bits"] == expected_bits, value
assert value["count"] == int(sys.argv[3]), value
if sys.argv[4] != "-":
    assert value["text"] == sys.argv[4], value
assert value["len"] == int(sys.argv[5]), value
assert value["first_zero"] == int(sys.argv[6]), value
assert value["first_one"] == int(sys.argv[7]), value
assert value["last_one"] == int(sys.argv[8]), value
assert value["trailing_zeros"] == int(sys.argv[9]), value
PY
}

value() {
  python3 - "$1" "$2" <<'PY'
import json
import sys

assert json.loads(sys.argv[1]) == {"value": json.loads(sys.argv[2])}
PY
}

invalid() {
  python3 - "$1" <<'PY'
import json
import sys

actual = json.loads(sys.argv[1])
assert actual["error_type"] == "InvalidInput", actual
assert "value" not in actual, actual
PY
}

snapshot "$(call '{"operation":"summary","args":[{"words":1,"positions":[1,4]},[6],[],[4]]}')" '[1,6]' 2 '1000010' 7 0 1 6 1
snapshot "$(call '{"operation":"summary","args":[{"words":2,"positions":[]},[63,64],[],[]]}')" '[63,64]' 2 - 65 0 63 64 63
value "$(call '{"operation":"has","args":[{"words":1,"positions":[0,63]},[0,1,63]]}')" '[true,false,true]'
snapshot "$(call '{"operation":"ranges","args":[{"words":2,"positions":[0,63,64,127]},[{"kind":"set","from":3,"to":66},{"kind":"reset","from":62,"to":65},{"kind":"flip","from":0,"to":4},{"kind":"reset_from","from":100,"to":128}]]}')" '[1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,65]' 61 - 66 0 1 65 1
value "$(call '{"operation":"search","args":[{"words":2,"positions":[0,63,65,127]},[0,1,62,63,64,65,126,127]]}')" '[{"start":0,"next_zero":1,"next_one":0},{"start":1,"next_zero":1,"next_one":63},{"start":62,"next_zero":62,"next_one":63},{"start":63,"next_zero":64,"next_one":63},{"start":64,"next_zero":64,"next_one":65},{"start":65,"next_zero":66,"next_one":65},{"start":126,"next_zero":126,"next_one":127},{"start":127,"next_zero":128,"next_one":127}]'
snapshot "$(call '{"operation":"shift","args":[{"words":2,"positions":[0,1,62,63,64,127]},"left",1]}')" '[1,2,63,64,65]' 5 - 66 0 1 65 1
snapshot "$(call '{"operation":"shift","args":[{"words":2,"positions":[0,1,63]},"left",64]}')" '[64,65,127]' 3 - 128 0 64 127 64
snapshot "$(call '{"operation":"shift","args":[{"words":2,"positions":[0,1,63,64,65,127]},"right",1]}')" '[0,62,63,64,126]' 5 - 127 1 0 126 0
snapshot "$(call '{"operation":"arithmetic","args":[{"words":1,"positions":[0,1]},"add",0]}')" '[2]' 1 '100' 3 0 2 2 2
snapshot "$(call '{"operation":"arithmetic","args":[{"words":1,"positions":[3]},"sub",0]}')" '[0,1,2]' 3 '111' 3 3 0 2 0
snapshot "$(call '{"operation":"relation","args":[{"words":2,"positions":[0,63,64]},{"words":2,"positions":[1,63,127]},"or"]}')" '[0,1,63,64,127]' 5 - 128 2 0 127 0
snapshot "$(call '{"operation":"relation","args":[{"words":2,"positions":[0,63,64]},{"words":2,"positions":[1,63,127]},"and"]}')" '[63]' 1 - 64 0 63 63 63
snapshot "$(call '{"operation":"relation","args":[{"words":2,"positions":[0,63,64]},{"words":2,"positions":[1,63,127]},"xor"]}')" '[0,1,64,127]' 4 - 128 2 0 127 0
value "$(call '{"operation":"relation","args":[{"words":1,"positions":[1,2]},{"words":1,"positions":[1,2]},"equals"]}')" 'true'
value "$(call '{"operation":"relation","args":[{"words":1,"positions":[1,2]},{"words":1,"positions":[1]},"has_subset"]}')" 'true'
value "$(call '{"operation":"relation","args":[{"words":1,"positions":[1]},{"words":1,"positions":[1,2]},"has_subset"]}')" 'false'
invalid "$(call '{"operation":"summary","args":[{"words":1,"positions":[64]},[],[],[]]}')"
invalid "$(call '{"operation":"ranges","args":[{"words":1,"positions":[]},[{"kind":"set","from":3,"to":65}]]}')"
invalid "$(call '{"operation":"unknown","args":[]}')"
