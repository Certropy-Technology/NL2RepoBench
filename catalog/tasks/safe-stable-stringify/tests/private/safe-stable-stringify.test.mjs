import { test } from 'node:test';
import assert from 'node:assert/strict';
import { call } from './test_client.mjs';

const expected = {
  'package-shape': { callable: true, configure: true, namedStringify: true, defaultAlias: true },
  'esm-wrapper': { defaultAlias: true, configure: true, output: '{"a":1,"b":2}' },
  'basic-order': '{"a":3,"b":[{"x":4,"y":5,"z":6},7],"c":8}',
  'nested-order': '{"a":[{"c":3,"d":4}],"z":{"a":1,"b":2}}',
  'array-order': '[{"a":1,"b":2},3,2]',
  'numeric-keys': '{"10":"ten","2":"two","a":"letter"}',
  'deterministic-false': '{"c":3,"b":2,"a":1}',
  'custom-comparator': '{"c":3,"b":2,"a":1}',
  'primitive-string': '"hello"', 'primitive-number': '42.5', 'primitive-boolean': 'false', 'primitive-null': 'null',
  'undefined-root': undefined, 'nonfinite': '{"a":null,"b":null,"c":null}',
  'escaping': '{"line":"\\n","quote":"\\\"","slash":"\\\\","unicode":"é"}',
  'unicode': '{"a":"é","z":"你好"}',
  'circular-default': '{"self":"[Circular]"}', 'circular-custom': '{"self":"<cycle>"}', 'circular-undefined': '{"keep":1}',
  'shared-reference': '{"a":{"q":1},"b":{"q":1}}',
  'bigint-default': '{"n":9007199254740993}', 'bigint-false': '{"keep":2}', 'bigint-string': '{"n":"9007199254740993"}',
  'tojson': '{"x":{"a":1,"b":2}}', 'replacer-parent': '{"a":1,"b":12}', 'replacer-omit': '{"keep":1}',
  'replacer-replace': '{"n":6}', 'replacer-root': '{"a":0,"z":1}', 'array-replacer': '{"b":2,"a":1}',
  'array-replacer-unique': '{"b":1,"0":0}', 'typed-replacer': '{"a":{"0":1},"b":3}',
  'space-string': '{\n  "a": {\n    "x": 1,\n    "y": 2\n  },\n  "b": 1\n}',
  'space-number': '{\n  "a": {\n    "x": 1,\n    "y": 2\n  },\n  "b": 1\n}',
  'space-cap': '{\n          "a": {\n                    "b": 1\n          }\n}',
  'space-zero': '{"a":2,"b":1}', 'empty-values': '{"a":{},"b":[]}',
  'typed-array': '{"0":0,"1":-1,"2":2}', 'typed-array-bigint': '{"a":{"0":"1","1":"2"}}',
  'maximum-depth': '{"a":{"a":"[Array]","b":"[Object]"}}',
  'maximum-breadth': '{"a":1,"b":2,"...":"1 item not stringified"}',
  'array-breadth': '["a","b","c","... 1 item not stringified"]',
  'safe-tojson': '{\n "a": "Error: Stringification failed with toJSON (Oops)"\n}',
  'safe-replacer': '{\n "a": 1,\n "b": "Error: Stringification failed (Oops)"\n}',
  'safe-getter': '"Error: Stringification failed (Oops)"',
  'configure-independent': ['{"n":2}', '{"n":"2"}', '{"a":1,"b":2}'],
};

const errors = {
  'bigint-invalid': /bigint/, 'circular-error': /Converting circular structure to JSON/, 'invalid-options': /maximumBreadth/,
  'strict-invalid': /type function/, 'strict-nan': /type number \(NaN\)/, 'strict-bigint': /type bigint \(5\)/,
  'strict-circular': /Converting circular structure to JSON/,
};

for (const [caseId, value] of Object.entries(expected)) {
  test(`safe-stable-stringify::${caseId}`, () => {
    const result = call(caseId);
    if (value === undefined) {
      assert.equal(result.kind, 'undefined');
      return;
    }
    assert.equal(result.kind, 'value');
    assert.deepEqual(result.value, value);
  });
}
for (const [caseId, pattern] of Object.entries(errors)) {
  test(`safe-stable-stringify::${caseId}`, () => {
    const result = call(caseId);
    assert.equal(result.kind, 'error');
    assert.match(result.message, pattern);
  });
}
