import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call, inventory, invoke} from './test_client.mjs';

const parseCookie = header => call('parseCookie', [header]);
const parseSetCookie = header => call('parseSetCookie', [header]);
const stringifyCookie = value => call('stringifyCookie', [value]);
const stringifySetCookie = value => call('stringifySetCookie', [value]);

function assertTypeError(method, args, message) {
	const response = invoke(method, args);
	assert.equal(response.ok, false);
	assert.equal(response.exceptionType, 'TypeError');
	assert.match(response.message, message);
}

test('package is scripts-free ESM with four named exports', () => {
	const response = inventory();
	assert.equal(response.ok, true);
	assert.deepEqual(response.value, {
		name: 'cookie',
		version: '2.0.1',
		type: 'module',
		runtimeDependencies: [],
		scriptNames: [],
		exports: {
			parseCookie: 'function',
			parseSetCookie: 'function',
			stringifyCookie: 'function',
			stringifySetCookie: 'function',
		},
	});
});

test('parseCookie parses one and multiple pairs', () => {
	assert.deepEqual(parseCookie('foo=bar'), {foo: 'bar'});
	assert.deepEqual(parseCookie('a=1; b=2'), {a: '1', b: '2'});
});

test('parseCookie ignores optional whitespace', () => {
	assert.deepEqual(parseCookie('FOO    = bar;   baz  =   raz'), {FOO: 'bar', baz: 'raz'});
	assert.deepEqual(parseCookie('\tfoo\t=\tbar\t'), {foo: 'bar'});
});

test('parseCookie handles empty input and minimum pairs', () => {
	assert.deepEqual(parseCookie(''), {});
	assert.deepEqual(parseCookie(' \t '), {});
	assert.deepEqual(parseCookie('f=;b='), {f: '', b: ''});
});

test('parseCookie decodes escapes and preserves malformed escapes', () => {
	assert.deepEqual(parseCookie('email=%20%22%2c%3b%2f'), {email: ' ",;/'});
	assert.deepEqual(parseCookie('foo=%1;bar=bar'), {foo: '%1', bar: 'bar'});
});

test('parseCookie trims names and keeps equals signs in values', () => {
	assert.deepEqual(parseCookie('  key  =  value=with=equals  '), {key: 'value=with=equals'});
	assert.deepEqual(parseCookie('   =   '), {'': ''});
});

test('parseCookie ignores fragments without an equals sign', () => {
	assert.deepEqual(parseCookie('foo=bar; fizz; buzz'), {foo: 'bar'});
	assert.deepEqual(parseCookie('fizz; foo=bar'), {foo: 'bar'});
});

test('parseCookie keeps the first duplicate value', () => {
	assert.deepEqual(parseCookie('foo=false;bar=bar;foo=true'), {foo: 'false', bar: 'bar'});
});

test('parseCookie preserves names inherited by ordinary objects', () => {
	assert.deepEqual(parseCookie('toString=foo;valueOf=bar'), {toString: 'foo', valueOf: 'bar'});
});

test('stringifyCookie serializes entries in object key order', () => {
	assert.equal(stringifyCookie({key: 'value'}), 'key=value');
	assert.equal(stringifyCookie({a: '1', b: '2'}), 'a=1; b=2');
});

test('stringifyCookie preserves empty values and empty objects', () => {
	assert.equal(stringifyCookie({}), '');
	assert.equal(stringifyCookie({a: '', b: ''}), 'a=; b=');
});

test('stringifyCookie percent-encodes unsafe value characters', () => {
	assert.equal(stringifyCookie({foo: 'bar baz'}), 'foo=bar%20baz');
	assert.equal(stringifyCookie({foo: 'foo,bar;100%'}), 'foo=foo%2Cbar%3B100%25');
});

test('stringifyCookie preserves roundtrip-safe cookie octets', () => {
	const value = "!#$&'()*+-./0123456789:<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~";
	assert.equal(stringifyCookie({foo: value}), `foo=${value}`);
});

test('stringifyCookie encodes BMP and astral Unicode', () => {
	assert.equal(stringifyCookie({key: 'cafe\u0301'}), 'key=cafe%CC%81');
	assert.equal(stringifyCookie({key: '\u{1F604}'}), 'key=%F0%9F%98%84');
});

test('stringifyCookie rejects invalid names', () => {
	for (const name of ['test=', 'foo bar', 'foo;bar', 'foo\tbar', 'foo\nbar']) {
		assertTypeError('stringifyCookie', [{[name]: 'value'}], /cookie name is invalid/);
	}
});

test('Cookie header stringify and parse roundtrip JSON string values', () => {
	for (const value of [
		{foo: 'bar', baz: 'qux'},
		{session: 'abc 123', token: 'x=y&z'},
		{foo: '%20'},
		{a: '', b: 'value'},
	]) assert.deepEqual(parseCookie(stringifyCookie(value)), value);
});

test('parseSetCookie handles ordinary, empty, and missing-name input', () => {
	assert.deepEqual(parseSetCookie('key=value'), {name: 'key', value: 'value'});
	assert.deepEqual(parseSetCookie('key='), {name: 'key', value: ''});
	assert.deepEqual(parseSetCookie('value'), {name: '', value: 'value'});
});

test('parseSetCookie trims, decodes, and keeps equals signs', () => {
	assert.deepEqual(parseSetCookie('\tkey\t=\tvalue%20with%20spaces\t'), {name: 'key', value: 'value with spaces'});
	assert.deepEqual(parseSetCookie('key=value=with=equals'), {name: 'key', value: 'value=with=equals'});
});

test('parseSetCookie ignores unknown and empty attributes', () => {
	assert.deepEqual(parseSetCookie('key=value;;; Unknown=x;; AnotherOne'), {name: 'key', value: 'value'});
});

test('parseSetCookie recognizes boolean attributes', () => {
	assert.deepEqual(parseSetCookie('key=value; HttpOnly=true; Secure=false; Partitioned'), {
		name: 'key', value: 'value', httpOnly: true, secure: true, partitioned: true,
	});
});

test('parseSetCookie accepts only integer max-age text', () => {
	assert.deepEqual(parseSetCookie('key=value; Max-Age=3600'), {name: 'key', value: 'value', maxAge: 3600});
	assert.deepEqual(parseSetCookie('key=value; Max-Age=-1'), {name: 'key', value: 'value', maxAge: -1});
	assert.deepEqual(parseSetCookie('key=value; Max-Age=1.5'), {name: 'key', value: 'value'});
	assert.deepEqual(parseSetCookie('key=value; Max-Age=123abc'), {name: 'key', value: 'value'});
});

test('parseSetCookie preserves domain and path attributes', () => {
	assert.deepEqual(parseSetCookie('key=value; Domain=example.com; Path=/some/path'), {
		name: 'key', value: 'value', domain: 'example.com', path: '/some/path',
	});
});

test('parseSetCookie normalizes valid same-site and priority values', () => {
	assert.deepEqual(parseSetCookie('key=value; SameSite=Lax; Priority=HIGH'), {
		name: 'key', value: 'value', sameSite: 'lax', priority: 'high',
	});
	assert.deepEqual(parseSetCookie('key=value; SameSite=Invalid; Priority=Invalid'), {name: 'key', value: 'value'});
});

test('parseSetCookie ignores invalid expires without projecting Date', () => {
	assert.deepEqual(parseSetCookie('key=value; Expires=InvalidDate'), {name: 'key', value: 'value'});
});

test('stringifySetCookie serializes, encodes, and normalizes empty values', () => {
	assert.equal(stringifySetCookie({name: 'foo', value: 'bar'}), 'foo=bar');
	assert.equal(stringifySetCookie({name: 'foo', value: 'bar +baz'}), 'foo=bar%20%2Bbaz');
	assert.equal(stringifySetCookie({name: 'foo', value: ''}), 'foo=');
	assert.equal(stringifySetCookie({name: 'foo', value: null}), 'foo=');
});

test('stringifySetCookie emits enabled flags in fixed order', () => {
	assert.equal(stringifySetCookie({
		name: 'foo', value: 'bar', httpOnly: true, secure: true, partitioned: true,
	}), 'foo=bar; HttpOnly; Secure; Partitioned');
});

test('stringifySetCookie serializes zero and negative max-age', () => {
	assert.equal(stringifySetCookie({name: 'foo', value: 'bar', maxAge: 0}), 'foo=bar; Max-Age=0');
	assert.equal(stringifySetCookie({name: 'foo', value: 'bar', maxAge: -1}), 'foo=bar; Max-Age=-1');
});

test('stringifySetCookie serializes valid domain and path', () => {
	assert.equal(stringifySetCookie({name: 'foo', value: 'bar', domain: '.example.com', path: '/login'}), 'foo=bar; Domain=.example.com; Path=/login');
});

test('stringifySetCookie normalizes priority and same-site', () => {
	assert.equal(stringifySetCookie({name: 'foo', value: 'bar', priority: 'High', sameSite: true}), 'foo=bar; Priority=High; SameSite=Strict');
	assert.equal(stringifySetCookie({name: 'foo', value: 'bar', priority: 'medium', sameSite: 'none'}), 'foo=bar; Priority=Medium; SameSite=None');
});

test('stringifySetCookie rejects invalid names', () => {
	for (const name of ['foo=bar', 'foo;bar', 'foo bar', 'foo\tbar', 'foo\n']) {
		assertTypeError('stringifySetCookie', [{name, value: 'bar'}], /argument name is invalid/);
	}
});

test('stringifySetCookie rejects invalid domain and path', () => {
	assertTypeError('stringifySetCookie', [{name: 'foo', value: 'bar', domain: 'domain..com'}], /option domain is invalid/);
	assertTypeError('stringifySetCookie', [{name: 'foo', value: 'bar', path: '/; Path=/sensitive'}], /option path is invalid/);
});

test('stringifySetCookie rejects invalid JSON-safe option values', () => {
	assertTypeError('stringifySetCookie', [{name: 'foo', value: 'bar', maxAge: 3.14}], /option maxAge is invalid/);
	assertTypeError('stringifySetCookie', [{name: 'foo', value: 'bar', priority: 'urgent'}], /option priority is invalid/);
	assertTypeError('stringifySetCookie', [{name: 'foo', value: 'bar', sameSite: 'sometimes'}], /option sameSite is invalid/);
});
