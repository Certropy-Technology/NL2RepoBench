#!/usr/bin/env bash
set -euo pipefail

BRIDGE=${1:?bridge executable is required}
PROXY=${2:?bridge proxy is required}

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

assert_case \
    list-array \
    '{"operation":"list","args":["array",[3,1,2],[{"name":"add","values":[4,5]},{"name":"insert","index":1,"values":[9,8]},{"name":"set","index":0,"value":7},{"name":"swap","index":1,"other":2},{"name":"remove","index":4},{"name":"sort"}]]}' \
    '{"value":{"contains_all":false,"contains_empty":true,"empty":false,"first":1,"first_ok":true,"index_of_one":0,"size":6,"string":"ArrayList\n1, 4, 5, 7, 8, 9","values":[1,4,5,7,8,9]}}'

for kind in singly doubly; do
    class_name=SinglyLinkedList
    [[ "$kind" == doubly ]] && class_name=DoublyLinkedList
    assert_case \
        "list-$kind" \
        "{\"operation\":\"list\",\"args\":[\"$kind\",[2,3],[{\"name\":\"prepend\",\"values\":[1]},{\"name\":\"append\",\"values\":[4]},{\"name\":\"insert\",\"index\":2,\"values\":[8]},{\"name\":\"remove\",\"index\":0}]]}" \
        "{\"value\":{\"contains_all\":false,\"contains_empty\":true,\"empty\":false,\"first\":2,\"first_ok\":true,\"index_of_one\":-1,\"size\":4,\"string\":\"$class_name\\n2, 8, 3, 4\",\"values\":[2,8,3,4]}}"
done

assert_case \
    stack-lifo \
    '{"operation":"stack","args":["linked",[1,2,3,4]]}' \
    '{"value":{"cleared_size":0,"empty":false,"peek":4,"peek_ok":true,"pop":4,"pop_ok":true,"size_after_pop":3,"values_after_pop":[3,2,1]}}'

assert_case \
    queue-fifo \
    '{"operation":"queue","args":["linked",[1,2,3,4]]}' \
    '{"value":{"cleared_size":0,"dequeue":1,"dequeue_ok":true,"empty":false,"peek":1,"peek_ok":true,"size_after_dequeue":3,"values_after_dequeue":[2,3,4]}}'

assert_case \
    circular-overwrite \
    '{"operation":"circular","args":[3,[1,2,3,4,5]]}' \
    '{"value":{"dequeue":3,"dequeue_ok":true,"full_after_dequeue":false,"full_before_dequeue":true,"peek":3,"peek_ok":true,"size":2,"values":[4,5]}}'

assert_case \
    hash-map \
    '{"operation":"map","args":["hash",[{"key":"b","value":2},{"key":"a","value":1},{"key":"a","value":9}]]}' \
    '{"value":{"empty":false,"get_a":9,"keys":["a","b"],"size":2,"values":[9,2]}}'

assert_case \
    linked-map \
    '{"operation":"map","args":["linked",[{"key":"b","value":2},{"key":"a","value":1},{"key":"b","value":9}]]}' \
    '{"value":{"empty":false,"keys":["b","a"],"size":2,"values":[9,1]}}'

assert_case \
    tree-map \
    '{"operation":"tree_map","args":[[{"key":1,"value":10},{"key":3,"value":30},{"key":2,"value":20}],[0,1,2,4]]}' \
    '{"value":{"keys":[1,2,3],"max":[3,30,true],"min":[1,10,true],"ranges":[{"ceiling":[1,10,true],"floor":[0,0,false]},{"ceiling":[1,10,true],"floor":[1,10,true]},{"ceiling":[2,20,true],"floor":[2,20,true]},{"ceiling":[0,0,false],"floor":[3,30,true]}],"values":[10,20,30]}}'

for kind in hash tree; do
    assert_case \
        "set-$kind" \
        "{\"operation\":\"set\",\"args\":[\"$kind\",[3,1,1,2],[2,3,4]]}" \
        '{"value":{"contains":true,"difference":[1],"intersection":[2,3],"size":3,"union":[1,2,3,4],"values":[1,2,3]}}'
done

assert_case \
    heap-order \
    '{"operation":"heap","args":[[4,1,3,2,1]]}' \
    '{"value":{"empty":true,"peek":1,"peek_ok":true,"pop_order":[1,1,2,3,4]}}'

assert_case \
    serialization \
    '{"operation":"serialization","args":["tree-set",[3,1,3,2]]}' \
    '{"value":{"json":"[1,2,3]","restored":[1,2,3]}}'

assert_case \
    empty-stack \
    '{"operation":"stack","args":["array",[]]}' \
    '{"value":{"cleared_size":0,"empty":true,"peek":0,"peek_ok":false,"pop":0,"pop_ok":false,"size_after_pop":0,"values_after_pop":[]}}'

assert_case \
    invalid-operation \
    '{"operation":"not-supported","args":[]}' \
    '{"error_type":"InvalidInput","message":"unknown operation"}'

assert_case \
    invalid-circular-capacity \
    '{"operation":"circular","args":[0,[]]}' \
    '{"error_type":"InvalidInput","message":"circular request exceeds bounds"}'
