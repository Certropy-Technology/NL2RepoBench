import assert from "node:assert/strict";
import { test } from "node:test";
import { request } from "./test_client.mjs";

const parse = (value, options = {}) => request("parse", value, options);
const noExceptions = (value, options = {}) => request("noExceptions", value, options);
const errorOf = (value, options = {}) => {
  try { parse(value, options); assert.fail("expected parse to throw"); }
  catch (error) { return error; }
};

const cases = [
  ["object result", () => assert.equal(parse('{"a":1}').json, '{"a":1}')],
  ["array result", () => assert.equal(parse('[1,"x",null]').json, '[1,"x",null]')],
  ["number result", () => assert.equal(parse('42.5'), 42.5)],
  ["boolean result", () => assert.equal(parse('true'), true)],
  ["null result", () => assert.equal(parse('null'), null)],
  ["empty string value", () => assert.equal(parse('""'), '')],
  ["unicode value", () => assert.equal(parse('"\u96ea\u82b1"'), '雪花')],
  ["nested values", () => assert.equal(parse('{"a":{"b":[1,2]}}').json, '{"a":{"b":[1,2]}}')],
  ["compact object metadata", () => { const x = parse('{"a":1}'); assert.equal(x.indent, ''); assert.equal(x.newline, ''); }],
  ["compact array metadata", () => { const x = parse('[1,2]'); assert.equal(x.indent, ''); assert.equal(x.newline, ''); }],
  ["two-space metadata", () => { const x = parse('{\n  "a": 1\n}'); assert.equal(x.indent, '  '); assert.equal(x.newline, '\n'); }],
  ["tab metadata", () => { const x = parse('{\n\t"a": 1\n}'); assert.equal(x.indent, '\t'); assert.equal(x.newline, '\n'); }],
  ["CRLF metadata", () => { const x = parse('{\r\n  "a": 1\r\n}'); assert.equal(x.indent, '  '); assert.equal(x.newline, '\r\n'); }],
  ["empty object defaults", () => { const x = parse('{}'); assert.equal(x.indent, '  '); assert.equal(x.newline, '\n'); }],
  ["empty array defaults", () => { const x = parse('[]'); assert.equal(x.indent, '  '); assert.equal(x.newline, '\n'); }],
  ["empty object source newline", () => { const x = parse('{}\r\n'); assert.equal(x.newline, '\r\n'); }],
  ["empty array source newline", () => { const x = parse('[]\n\n'); assert.equal(x.newline, '\n\n'); }],
  ["buffer input", () => assert.equal(parse({ type: "buffer", base64: Buffer.from('{"a":1}').toString("base64") }).json, '{"a":1}')],
  ["buffer BOM input", () => assert.equal(parse({ type: "buffer", base64: Buffer.from('\ufeff{"a":1}').toString("base64") }).json, '{"a":1}')],
  ["string BOM input", () => assert.equal(parse('\ufeff[1,2]').json, '[1,2]')],
  ["invalid token error", () => { const e = errorOf('garbage'); assert.equal(e.error_type, 'JSONParseError'); assert.match(e.message, /while parsing/); }],
  ["error code", () => assert.equal(errorOf('garbage').code, 'EJSONPARSE')],
  ["error name", () => assert.equal(errorOf('garbage').name, 'JSONParseError')],
  ["error position", () => assert.equal(typeof errorOf('garbage').position, 'number')],
  ["error system type", () => assert.equal(errorOf('garbage').systemError, 'SyntaxError')],
  ["error context short", () => assert.match(errorOf('abcde', { context: 2 }).message, /while parsing/)],
  ["error context bounded", () => assert.ok(errorOf('x'.repeat(10000), { context: 2 }).message.length < 500)],
  ["empty input error", () => assert.match(errorOf('').message, /empty string/)],
  ["unexpected end error", () => assert.match(errorOf('{"a":').message, /while parsing/)],
  ["non-string undefined error", () => { const e = errorOf({ type: 'undefined' }); assert.equal(e.error_type, 'TypeError'); assert.equal(e.code, 'EJSONPARSE'); }],
  ["number coercion follows JSON.parse", () => assert.equal(parse(12), 12)],
  ["non-string object error", () => assert.equal(errorOf({ a: 1 }).error_type, 'TypeError')],
  ["empty array error", () => assert.match(errorOf({ type: 'empty-array' }).message, /empty array/)],
  ["map error", () => assert.equal(errorOf({ type: 'map' }).error_type, 'TypeError')],
  ["date error", () => assert.equal(errorOf({ type: 'date' }).error_type, 'TypeError')],
  ["noExceptions invalid", () => assert.deepEqual(noExceptions('garbage'), { type: 'undefined' })],
  ["noExceptions valid", () => assert.equal(noExceptions('{"ok":true}').json, '{"ok":true}')],
  ["noExceptions buffer", () => assert.equal(noExceptions({ type: 'buffer', base64: Buffer.from('[1]').toString('base64') }).json, '[1]')],
  ["noExceptions BOM", () => assert.equal(noExceptions('\ufefftrue'), true)],
  ["noExceptions undefined", () => assert.deepEqual(noExceptions({ type: 'undefined' }), { type: 'undefined' })],
  ["delete reviver", () => assert.equal(parse('{"keep":1,"secret":2}', { reviver: 'deleteSecret' }).json, '{"keep":1}')],
  ["double reviver", () => assert.equal(parse('{"n":2}', { reviver: 'doubleNumbers' }).json, '{"n":4}')],
  ["reviver array", () => assert.equal(parse('[1,2]', { reviver: 'doubleNumbers' }).json, '[2,4]')],
  ["primitive has no indent", () => assert.equal(parse('"x"').indent, undefined)],
  ["primitive has no newline", () => assert.equal(parse('1').newline, undefined)],
  ["metadata newline preserves repeated LF", () => assert.equal(parse('{\n\n  "a": 1\n\n}').newline, '\n\n')],
  ["metadata indent preserves mixed whitespace", () => assert.equal(parse('{\n \t "a": 1\n}').indent, ' \t ')],
  ["class extends SyntaxError", () => assert.equal(request('class', null, { text: 'abc' }).isSyntaxError, true)],
  ["class name stable", () => assert.equal(request('class', null, { text: 'abc' }).name, 'JSONParseError')],
  ["class code", () => assert.equal(request('class', null, { text: 'abc' }).code, 'EJSONPARSE')],
  ["class retains system error", () => assert.equal(request('class', null, { text: 'abc' }).sameError, true)],
  ["class tag", () => assert.equal(request('class', null, { text: 'abc' }).tag, 'JSONParseError')],
  ["class message context", () => assert.match(request('class', null, { text: 'abc' }).message, /while parsing/)],
  ["class default position", () => assert.equal(request('class', null, { text: 'abc' }).position, 0)],
  ["negative number", () => assert.equal(parse('-3'), -3)],
  ["exponent number", () => assert.equal(parse('1e3'), 1000)],
  ["escaped string", () => assert.equal(parse('"a\\nb"'), 'a\nb')],
  ["false result", () => assert.equal(parse('false'), false)],
  ["large valid input", () => assert.equal(parse(JSON.stringify({ value: 'a'.repeat(1000) })).json.length > 1000, true)],
  ["error includes excerpt", () => assert.match(errorOf('{"key": bad}').message, /while parsing/)],
];

for (const [name, body] of cases) test(name, body);
assert.equal(cases.length, 60);
