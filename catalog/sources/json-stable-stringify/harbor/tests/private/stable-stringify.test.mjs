import { test } from 'node:test';
import assert from 'node:assert/strict';
import { call } from './test_client.mjs';

const cases = [
  ['basic', 'value', '{"a":3,"b":[{"x":4,"y":5,"z":6},7],"c":8}'],
  ['nested', 'value', '{"a":[{"c":3,"d":4}],"z":{"a":1,"b":2}}'],
  ['array-order', 'value', '[{"a":1,"b":2},3,2]'],
  ['string', 'value', '"hello"'], ['number', 'value', '42.5'], ['boolean', 'value', 'false'],
  ['null', 'value', 'null'], ['undefined-root', 'undefined', undefined], ['nan', 'value', 'null'],
  ['infinity', 'value', 'null'], ['undefined-property', 'value', '{"keep":1}'],
  ['undefined-array', 'value', '[1,null,3]'], ['to-json', 'value', '{"a":1,"z":2}'],
  ['numeric-keys', 'value', '{"10":"ten","2":"two","a":"letter"}'],
  ['escaping', 'value', '{"line":"\\n","quote":"\\\"","slash":"\\\\"}'],
  ['space-string', 'value', '{\n  "a": {\n    "x": 1,\n    "y": 2\n  },\n  "b": 1\n}'],
  ['space-number', 'value', '{\n  "a": {\n    "x": 1,\n    "y": 2\n  },\n  "b": 1\n}'], ['space-zero', 'value', '{"a":2,"b":1}'],
  ['empty-object', 'value', '{}'], ['empty-array', 'value', '[]'],
  ['collapse-empty', 'value', '{\n  "a": {},\n  "b": []\n}'],
  ['pretty-empty', 'value', '{\n  "a": {\n  },\n  "b": [\n  ]\n}'],
  ['reverse-cmp', 'value', '{"c":3,"b":2,"a":1}'], ['value-cmp', 'value', '{"a":10,"d":6,"c":5,"b":3}'],
  ['get-cmp', 'value', '{"b":1,"a":2,"c":3}'], ['direct-cmp', 'value', '{"a":1,"b":2,"c":3}'],
  ['tie-cmp', 'value', '{"c":3,"b":2,"a":1}'], ['replacer-parent', 'value', '{"a":1,"b":12}'],
  ['replacer-omit', 'value', '{"keep":1}'], ['replacer-replace', 'value', '{"n":6}'],
  ['replacer-root', 'value', '{"a":0,"z":1}'], ['cycle-error', 'error', 'Converting circular structure to JSON'],
  ['cycle-value', 'value', '{"self":"__cycle__"}'], ['shared-reference', 'value', '{"a":{"q":1},"b":{"q":1}}'],
  ['null-prototype', 'value', '{"a":1,"b":2}'], ['inherited', 'value', '{"own":2}'],
  ['symbol', 'value', '{"a":1,"b":2}'], ['non-enumerable', 'value', '{"a":1}'],
  ['date', 'value', '"2020-01-02T03:04:05.000Z"'], ['bigint', 'error', 'Do not know how to serialize a BigInt'],
  ['collapse-type-string', 'error', '`collapseEmpty` must be a boolean, if provided'],
  ['collapse-type-null', 'error', '`collapseEmpty` must be a boolean, if provided'],
  ['cmp-values', 'value', '{"b":1,"aa":2,"ccc":3}'], ['no-options', 'value', '{"a":1,"b":2}'],
  ['null-options', 'error', 'The comparison function must be either a function or undefined: null'], ['long-space', 'value', '{\n            "a": 1\n}'],
  ['nested-empty', 'value', '{"outer":{"a":[],"z":{}}}'], ['property-to-json', 'value', '{"a":1,"x":5}'],
  ['replacer-array', 'value', '[1,20,3]'], ['nested-cycle', 'value', '{"child":{"parent":"__cycle__"}}'],
  ['unicode', 'value', '{"a":"é","z":"你好"}'], ['negative-zero', 'value', '0'],
];

for (const [caseId, kind, expected] of cases) {
  test(caseId, () => {
    const result = call(caseId);
    assert.equal(result.kind, kind);
    if (kind === 'error') assert.match(result.message, new RegExp(expected.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    else if (kind === 'undefined') assert.equal(result.value, undefined);
    else assert.equal(result.value, expected);
  });
}
