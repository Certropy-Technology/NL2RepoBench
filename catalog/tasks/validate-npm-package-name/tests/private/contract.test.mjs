import assert from 'node:assert/strict';
import test from 'node:test';
import {callCandidate, callSpecial, inspectPackage} from './test_client.mjs';

const valid = () => ({validForNewPackages: true, validForOldPackages: true});
const warning = (...warnings) => ({
  validForNewPackages: false,
  validForOldPackages: true,
  warnings,
});
const error = (...errors) => ({
  validForNewPackages: false,
  validForOldPackages: false,
  errors,
});

function responseValue(response) {
  assert.equal(response.ok, true, JSON.stringify(response));
  return response.value;
}

function check(input, expected) {
  assert.deepEqual(responseValue(callCandidate(input)), expected);
}

function checkSpecial(inputType, expected) {
  assert.deepEqual(responseValue(callSpecial(inputType)), expected);
}

test('package metadata and CommonJS root export are correct', () => {
  assert.deepEqual(responseValue(inspectPackage()), {
    name: 'validate-npm-package-name',
    version: '8.0.0',
    callable: true,
  });
});

test('ordinary lowercase package names are valid', () => {
  for (const name of ['validate-npm-package-name', 'some-package', 'abc']) check(name, valid());
});

test('period underscore and numeric names are valid', () => {
  for (const name of ['example.com', 'under_score', 'period.js', '123numeric']) check(name, valid());
});

test('ordinary scoped names are valid', () => {
  for (const name of ['@npm/thingy', '@npm-zors/money-time.js', '@a/b']) check(name, valid());
});

test('empty string reports the length error', () => {
  check('', error('name length must be greater than zero'));
});

test('null reports its dedicated error', () => {
  check(null, error('name cannot be null'));
});

test('undefined reports its dedicated error', () => {
  checkSpecial('undefined', error('name cannot be undefined'));
});

test('finite and non-finite numbers must be strings', () => {
  check(42, error('name must be a string'));
  for (const kind of ['nan', 'infinity', 'negative-infinity']) {
    checkSpecial(kind, error('name must be a string'));
  }
});

test('booleans must be strings', () => {
  check(true, error('name must be a string'));
  check(false, error('name must be a string'));
});

test('arrays and objects must be strings', () => {
  check([], error('name must be a string'));
  check({}, error('name must be a string'));
});

test('bigint symbol and function values must be strings', () => {
  for (const kind of ['bigint', 'symbol', 'function']) {
    checkSpecial(kind, error('name must be a string'));
  }
});

test('unscoped names cannot start with a period', () => {
  check('.start-with-period', error('name cannot start with a period'));
});

test('scoped package segment cannot start with a period', () => {
  for (const name of ['@npm/.', '@npm/..', '@npm/.package']) {
    check(name, error('name cannot start with a period'));
  }
});

test('unscoped names cannot start with a hyphen', () => {
  check('-start-with-hyphen', error('name cannot start with a hyphen'));
  check('--double-hyphen', error('name cannot start with a hyphen'));
});

test('unscoped names cannot start with an underscore', () => {
  check('_start-with-underscore', error('name cannot start with an underscore'));
});

test('leading spaces preserve error order', () => {
  check(' leading-space', error(
    'name cannot contain leading or trailing spaces',
    'name can only contain URL-friendly characters',
  ));
});

test('trailing spaces preserve error order', () => {
  check('trailing-space ', error(
    'name cannot contain leading or trailing spaces',
    'name can only contain URL-friendly characters',
  ));
});

test('embedded whitespace is not URL friendly', () => {
  check('two words', error('name can only contain URL-friendly characters'));
  check('two\twords', error('name can only contain URL-friendly characters'));
});

test('multiple slashes are not a valid scope form', () => {
  check('s/l/a/s/h/e/s', error('name can only contain URL-friendly characters'));
});

test('colon and percent characters are not URL friendly', () => {
  check('contain:colons', error('name can only contain URL-friendly characters'));
  check('percent%name', error('name can only contain URL-friendly characters'));
});

test('non-ASCII names are not URL friendly', () => {
  check('cafe-\u00e9', error('name can only contain URL-friendly characters'));
});

test('node_modules is excluded case insensitively', () => {
  check('node_modules', error('node_modules is not a valid package name'));
});

test('favicon.ico is excluded case insensitively', () => {
  check('favicon.ico', error('favicon.ico is not a valid package name'));
});

test('mixed-case excluded names retain both errors and warnings', () => {
  check('Node_Modules', {
    validForNewPackages: false,
    validForOldPackages: false,
    warnings: ['name can no longer contain capital letters'],
    errors: ['node_modules is not a valid package name'],
  });
});

test('bare http core module is a legacy warning', () => {
  check('http', warning('http is a core module name'));
});

test('other bare core modules are legacy warnings', () => {
  for (const name of ['fs', 'path', 'stream', 'util']) {
    check(name, warning(`${name} is a core module name`));
  }
});

test('node-prefixed builtins retain warning and URL error', () => {
  check('node:test', {
    validForNewPackages: false,
    validForOldPackages: false,
    warnings: ['node:test is a core module name'],
    errors: ['name can only contain URL-friendly characters'],
  });
});

test('exactly 214 UTF-16 code units are accepted', () => {
  check('a'.repeat(214), valid());
});

test('more than 214 UTF-16 code units is a legacy warning', () => {
  check('a'.repeat(215), warning('name can no longer contain more than 214 characters'));
});

test('capital letters are a legacy warning', () => {
  check('CAPITAL-LETTERS', warning('name can no longer contain capital letters'));
});

test('special characters in the package segment are legacy warnings', () => {
  for (const character of ['~', "'", '!', '(', ')', '*']) {
    check(`name${character}`, warning('name can no longer contain special characters ("~\'!()*")'));
  }
});

test('combined warnings use length capitals special order', () => {
  const name = `A${'a'.repeat(213)}!`;
  check(name, warning(
    'name can no longer contain more than 214 characters',
    'name can no longer contain capital letters',
    'name can no longer contain special characters ("~\'!()*")',
  ));
});

test('special-character warning checks only the final scoped segment', () => {
  check('@scope!/package', valid());
  check('@scope/package!', warning('name can no longer contain special characters ("~\'!()*")'));
});

test('scoped package segment may start with hyphen or underscore', () => {
  check('@user/-package', valid());
  check('@user/_package', valid());
});

test('scoped package segment may equal excluded names', () => {
  check('@user/node_modules', valid());
  check('@user/favicon.ico', valid());
});

test('scoped package segment may equal a core module name', () => {
  check('@user/http', valid());
  check('@user/fs', valid());
});

test('empty scope or package segments are malformed', () => {
  check('@/package', error('name can only contain URL-friendly characters'));
  check('@scope/', error('name can only contain URL-friendly characters'));
});

test('extra scoped path segments are malformed', () => {
  check('@scope/pkg/extra', error('name can only contain URL-friendly characters'));
});

test('non-ASCII scoped segments are not URL friendly', () => {
  check('@sc\u00f8pe/package', error('name can only contain URL-friendly characters'));
  check('@scope/p\u00e4ckage', error('name can only contain URL-friendly characters'));
});

test('URL-safe dots underscores and hyphens work in both scoped segments', () => {
  check('@scope-name_1/pkg.name_2', valid());
});

test('valid results omit warnings and errors', () => {
  assert.deepEqual(Object.keys(responseValue(callCandidate('plain-name'))), [
    'validForNewPackages', 'validForOldPackages',
  ]);
});

test('warning-only results omit errors', () => {
  const result = responseValue(callCandidate('Upper'));
  assert.equal(Object.hasOwn(result, 'warnings'), true);
  assert.equal(Object.hasOwn(result, 'errors'), false);
});

test('error-only results omit warnings', () => {
  const result = responseValue(callCandidate('two words'));
  assert.equal(Object.hasOwn(result, 'warnings'), false);
  assert.equal(Object.hasOwn(result, 'errors'), true);
});

test('repeated mixed calls are deterministic and stateless', () => {
  const inputs = ['plain-name', 'http', '.bad', '@scope/pkg', 'plain-name'];
  const expected = [
    valid(),
    warning('http is a core module name'),
    error('name cannot start with a period'),
    valid(),
    valid(),
  ];
  assert.deepEqual(inputs.map(input => responseValue(callCandidate(input))), expected);
});
