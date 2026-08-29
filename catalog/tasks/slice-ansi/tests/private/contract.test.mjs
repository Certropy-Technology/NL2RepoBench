import assert from 'node:assert/strict';
import {test} from 'node:test';
import {callCandidate} from './test_client.mjs';

const ESC = '\x1B';
const BEL = '\x07';
const ST = `${ESC}\\`;
const C1_OSC = '\x9D';
const C1_ST = '\x9C';
const red = text => `${ESC}[31m${text}${ESC}[39m`;
const bold = text => `${ESC}[1m${text}${ESC}[22m`;

test('package root exposes an ESM default callable', () => {
  assert.equal(callCandidate('abcdef', 1, 4), 'bcd');
});

test('plain slices preserve visible text and omitted end', () => {
  assert.equal(callCandidate('The quick brown fox', 4, 9), 'quick');
  assert.equal(callCandidate('The quick brown fox', 10), 'brown fox');
  assert.equal(callCandidate('text', 2, 2), '');
});

test('out-of-range and reversed boundaries produce an empty slice', () => {
  assert.equal(callCandidate('text', 20, 30), '');
  assert.equal(callCandidate('text', 3, 2), '');
});

test('simple SGR styles are retained and closed', () => {
  assert.equal(callCandidate(red('hello world'), 0, 5), red('hello'));
  assert.equal(callCandidate(`${red('red')} tail`, 4, 8), 'tail');
});

test('active styles survive a slice that starts after the opening code', () => {
  const input = `plain ${red('colored')} end`;
  assert.equal(callCandidate(input, 7, 10), red('olo'));
  assert.equal(callCandidate(bold(red('text')), 0, 2), `${ESC}[1m${ESC}[31mte${ESC}[39m${ESC}[22m`);
});

test('background and foreground state closes in reverse order', () => {
  const input = `${ESC}[42m${ESC}[30mtest${ESC}[39m${ESC}[49m`;
  assert.equal(callCandidate(input, 0, 2), `${ESC}[42m${ESC}[30mte${ESC}[39m${ESC}[49m`);
});

test('non-SGR CSI and control strings do not count as visible columns', () => {
  const input = `${ESC}[2Jabc${ESC}[?25l`;
  assert.equal(callCandidate(input, 0, 3), 'abc');
  assert.equal(callCandidate(`${ESC}]0;title${BEL}abc`, 1, 3), 'bc');
});

test('malformed control prefixes do not swallow following text', () => {
  assert.equal(callCandidate(`${ESC}[31`, 0, 3), '');
  assert.equal(callCandidate(`${ESC}[31xabc`, 0, 3), 'abc');
});

test('truecolor and colon SGR controls remain non-visible', () => {
  const input = `${ESC}[38;2;255;0;0mred${ESC}[39m`;
  assert.equal(callCandidate(input, 0, 2), `${ESC}[38;2;255;0;0mre${ESC}[39m`);
  const colon = `${ESC}[38:2:255:0:0mred${ESC}[39m`;
  assert.equal(callCandidate(colon, 0, 1), `${ESC}[38:2:255:0:0mr${ESC}[39m`);
});

test('fullwidth characters occupy two columns and are not split', () => {
  assert.equal(callCandidate('AあB', 0, 2), 'A');
  assert.equal(callCandidate('AあB', 1, 3), 'あ');
  assert.equal(callCandidate('あいう', 0, 3), 'あ');
});

test('surrogate pairs and combining marks remain intact', () => {
  assert.equal(callCandidate('a😀BC', 0, 2), 'a');
  assert.equal(callCandidate('a😀BC', 0, 3), 'a😀');
  assert.equal(callCandidate('AéB', 1, 2), 'é');
});

test('ZWJ emoji graphemes are kept together', () => {
  const family = 'A👨‍👩‍👧‍👦B';
  assert.equal(callCandidate(family, 1, 3), '👨‍👩‍👧‍👦');
  assert.equal(callCandidate(family, 3, 4), 'B');
});

test('CRLF is preserved as one grapheme cluster', () => {
  assert.equal(callCandidate('A\r\nB', 1, 2), '\r\n');
  assert.equal(callCandidate('A\r\nB', 2, 3), 'B');
});

test('regional indicators, keycaps, and emoji presentation are wide graphemes', () => {
  assert.equal(callCandidate('A🇮🇱B', 1, 3), '🇮🇱');
  assert.equal(callCandidate('A1️⃣B', 1, 3), '1️⃣');
  assert.equal(callCandidate('A☺️B', 1, 3), '☺️');
});

test('styled wide and emoji graphemes respect the end boundary', () => {
  assert.equal(callCandidate(`${red('あ')}B`, 0, 1), '');
  assert.equal(callCandidate(`${red('あ')}B`, 0, 2), red('あ'));
  assert.equal(callCandidate(`${red('☺️')}B`, 0, 1), '');
});

test('styles inserted within a grapheme do not split the grapheme', () => {
  const input = `${red('e')}́B`;
  assert.equal(callCandidate(input, 0, 1), `${red('e')}́`);
  assert.equal(callCandidate(input, 1, 2), 'B');
});

test('regional-indicator slices skip internal visible boundaries', () => {
  const input = 'A🇮🇱B';
  assert.equal(callCandidate(input, 1, 2), '');
  assert.equal(callCandidate(input, 2, 3), '');
  assert.equal(callCandidate(input, 3, 4), 'B');
});

test('OSC-8 hyperlinks with BEL are preserved for non-empty slices', () => {
  const link = `${ESC}]8;;https://example.com${BEL}Google${ESC}]8;;${BEL}`;
  assert.equal(callCandidate(link, 0, 6), link);
  assert.equal(callCandidate(link, 1, 4), `${ESC}]8;;https://example.com${BEL}oog${ESC}]8;;${BEL}`);
});

test('OSC-8 hyperlinks support ESC-ST and parameters', () => {
  const link = `${ESC}]8;id=abc;https://example.com${ST}Google${ESC}]8;;${ST}`;
  assert.equal(callCandidate(link, 2), `${ESC}]8;id=abc;https://example.com${ST}ogle${ESC}]8;;${ST}`);
});

test('C1 OSC-8 hyperlinks support BEL and C1-ST', () => {
  const bel = `${C1_OSC}8;;https://example.com${BEL}Go${C1_OSC}8;;${BEL}`;
  const c1 = `${C1_OSC}8;;https://example.com${C1_ST}Go${C1_OSC}8;;${C1_ST}`;
  assert.equal(callCandidate(bel, 0, 2), bel);
  assert.equal(callCandidate(c1, 1, 2), `${C1_OSC}8;;https://example.com${C1_ST}o${C1_OSC}8;;${C1_ST}`);
});

test('empty hyperlink selections do not emit hyperlink controls', () => {
  const link = `${ESC}]8;;https://example.com${BEL}Google${ESC}]8;;${BEL}`;
  assert.equal(callCandidate(link, 2, 2), '');
  assert.equal(callCandidate(`${link}tail`, 6, 7), 't');
});

test('hyperlink and style nesting preserves both active states', () => {
  const open = `${ESC}]8;;https://example.com${BEL}`;
  const close = `${ESC}]8;;${BEL}`;
  const input = `${red(open + 'A' + close + 'B')}`;
  assert.equal(callCandidate(input, 0, 2), `${ESC}[31m${open}A${close}B${ESC}[39m`);
});

test('ordinary text remains unchanged around control sequences', () => {
  const input = `left${ESC}[31mred${ESC}[39m${ESC}]0;ignored${BEL}right`;
  assert.equal(callCandidate(input, 0, 11), `left${ESC}[31mred${ESC}[39m${ESC}]0;ignored${BEL}righ`);
});

test('mixed calls are stateless and deterministic', () => {
  const inputs = [['abc', 0, 2], [red('あいう'), 1, 3], ['éx', 0, 1], ['abc', 2]];
  const first = inputs.map(args => callCandidate(...args));
  const second = inputs.map(args => callCandidate(...args));
  assert.deepEqual(second, first);
});
