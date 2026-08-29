import assert from 'node:assert/strict';
import {test} from 'node:test';
import {format, inventory, support} from './test_client.mjs';

const esc = '\u001B';
const step = name => ({name, args: []});
const styled = (enabled, steps, values) => format({enabled, steps, values});

test('TC-01 package metadata and CommonJS entry are complete', () => {
  const value = inventory();
  assert.equal(value.name, 'picocolors');
  assert.equal(value.version, '1.1.1');
  assert.equal(value.main, './picocolors.js');
  assert.deepEqual(value.browser, {'./picocolors.js': './picocolors.browser.js'});
  assert.deepEqual(value.files, ['picocolors.*', 'types.d.ts']);
});

test('TC-02 root exports the factory, support flag, and all formatter families', () => {
  const value = inventory();
  assert.equal(typeof value.support, 'boolean');
  assert.equal(value.factoryFalse, false);
  assert.equal(value.factoryTrue, true);
  assert.ok(value.keys.includes('createColors'));
  assert.ok(value.keys.includes('red'));
  assert.ok(value.keys.includes('bgWhiteBright'));
});

test('TC-03 createColors false disables every formatter', () => {
  assert.equal(styled(0, [step('red')], ['plain']), 'plain');
  assert.equal(styled(0, [step('bold')], ['plain']), 'plain');
  assert.equal(styled(0, [step('bgBlueBright')], ['plain']), 'plain');
});

test('TC-04 createColors true enables every formatter', () => {
  assert.equal(styled(1, [step('red')], ['plain']), `${esc}[31mplain${esc}[39m`);
  assert.equal(styled(1, [step('bold')], ['plain']), `${esc}[1mplain${esc}[22m`);
  assert.equal(styled(1, [step('bgBlueBright')], ['plain']), `${esc}[104mplain${esc}[49m`);
});

test('TC-05 formatter coercion preserves JavaScript string conversion', () => {
  assert.equal(styled(1, [step('red')], []), `${esc}[31mundefined${esc}[39m`);
  assert.equal(styled(1, [step('red')], [null]), `${esc}[31mnull${esc}[39m`);
  assert.equal(styled(1, [step('red')], [42]), `${esc}[31m42${esc}[39m`);
  assert.equal(styled(1, [step('red')], [true]), `${esc}[31mtrue${esc}[39m`);
  assert.equal(styled(1, [step('red')], [['a', 'b']]), `${esc}[31ma,b${esc}[39m`);
  assert.equal(styled(1, [step('red')], [{x: 1}]), `${esc}[31m[object Object]${esc}[39m`);
});

test('TC-06 modifier ANSI pairs match the documented contract', () => {
  const pairs = [['reset', 0, 0], ['dim', 2, 22], ['italic', 3, 23], ['underline', 4, 24], ['inverse', 7, 27], ['hidden', 8, 28], ['strikethrough', 9, 29]];
  for (const [name, open, close] of pairs) assert.equal(styled(1, [step(name)], ['x']), `${esc}[${open}mx${esc}[${close}m`);
});

test('TC-07 standard foreground colors use SGR 30 through 37 and gray 90', () => {
  const values = [['black', 30], ['red', 31], ['green', 32], ['yellow', 33], ['blue', 34], ['magenta', 35], ['cyan', 36], ['white', 37], ['gray', 90]];
  for (const [name, code] of values) assert.equal(styled(1, [step(name)], ['x']), `${esc}[${code}mx${esc}[39m`);
});

test('TC-08 bright foreground colors use SGR 90 through 97', () => {
  const names = ['blackBright', 'redBright', 'greenBright', 'yellowBright', 'blueBright', 'magentaBright', 'cyanBright', 'whiteBright'];
  names.forEach((name, index) => assert.equal(styled(1, [step(name)], ['x']), `${esc}[${90 + index}mx${esc}[39m`));
});

test('TC-09 backgrounds use normal and bright SGR pairs', () => {
  assert.equal(styled(1, [step('bgRed')], ['x']), `${esc}[41mx${esc}[49m`);
  assert.equal(styled(1, [step('bgWhite')], ['x']), `${esc}[47mx${esc}[49m`);
  assert.equal(styled(1, [step('bgBlackBright')], ['x']), `${esc}[100mx${esc}[49m`);
  assert.equal(styled(1, [step('bgWhiteBright')], ['x']), `${esc}[107mx${esc}[49m`);
});

test('TC-10 nested formatters preserve open order and reverse close order', () => {
  assert.equal(styled(1, [step('red'), step('bold'), step('underline')], ['x']), `${esc}[31m${esc}[1m${esc}[4mx${esc}[24m${esc}[22m${esc}[39m`);
});

test('TC-11 an inner close sequence reopens the outer formatter', () => {
  assert.equal(styled(1, [step('red')], [`a${esc}[32mb${esc}[39mc`]), `${esc}[31ma${esc}[32mb${esc}[31mc${esc}[39m`);
});

test('TC-12 large already-colored input remains bounded', () => {
  const value = styled(1, [step('blue')], [`${esc}[31m${'x'.repeat(10000)}${esc}[39m`]);
  assert.equal(typeof value, 'string');
  assert.ok(value.length < 20050);
});

test('TC-13 factory results are fresh and do not mutate the default object', () => {
  const value = inventory();
  assert.equal(value.factoryFalse, false);
  assert.equal(value.factoryTrue, true);
  assert.notEqual(value.factoryFalse, value.factoryTrue);
});

test('TC-14 browser entry is disabled and stringifies input', () => {
  const value = inventory();
  assert.equal(value.browserSupport, false);
  assert.equal(value.browserRed, 'x');
  assert.ok(value.browserKeys.includes('createColors'));
});

test('TC-15 empty strings are still wrapped when enabled', () => {
  assert.equal(styled(1, [step('green')], ['']), `${esc}[32m${esc}[39m`);
  assert.equal(styled(0, [step('green')], ['']), '');
});

test('TC-16 text and existing ANSI escapes are preserved except for formatter reopening', () => {
  const value = `line 1\nline 2\r\n${esc}[1mraw${esc}[22m`;
  assert.equal(styled(0, [step('cyan')], [value]), value);
});

test('TC-17 isolated baseline reports no support', () => {
  assert.equal(support({env: {TERM: 'dumb', LC_ALL: 'C.UTF-8'}, argv: []}), false);
});

test('TC-18 CI enables support when no disabling signal is present', () => {
  assert.equal(support({env: {TERM: 'dumb', CI: 'true'}, argv: []}), true);
});

test('TC-19 FORCE_COLOR enables support', () => {
  assert.equal(support({env: {TERM: 'dumb', FORCE_COLOR: '1'}, argv: []}), true);
});

test('TC-20 NO_COLOR disables support even with FORCE_COLOR', () => {
  assert.equal(support({env: {TERM: 'xterm', FORCE_COLOR: '1', NO_COLOR: '1'}, argv: []}), false);
});

test('TC-21 --color enables support', () => {
  assert.equal(support({env: {TERM: 'dumb'}, argv: ['node', '--color']}), true);
});

test('TC-22 --no-color disables support even with FORCE_COLOR', () => {
  assert.equal(support({env: {TERM: 'xterm', FORCE_COLOR: '1'}, argv: ['node', '--no-color']}), false);
});

test('TC-23 a non-dumb TTY enables support', () => {
  assert.equal(support({env: {TERM: 'xterm'}, argv: [], stdoutTTY: true}), true);
});

test('TC-24 Windows enables support without a TTY', () => {
  assert.equal(support({env: {TERM: 'dumb'}, argv: [], platform: 'win32'}), true);
});
