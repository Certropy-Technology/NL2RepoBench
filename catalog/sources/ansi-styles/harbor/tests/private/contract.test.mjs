import assert from 'node:assert/strict';
import {test} from 'node:test';
import {convert, group, inventory, style} from './test_client.mjs';

const esc = '\u001B';

test('package metadata and ESM entry are complete', () => {
  const value = inventory();
  assert.deepEqual({name: value.packageName, version: value.packageVersion, type: value.type}, {
    name: 'ansi-styles', version: '7.0.0', type: 'module',
  });
  assert.equal(value.packageExport, './index.js');
  assert.equal(value.hasDeclaration, true);
});

test('documented name arrays have stable order', () => {
  const value = inventory();
  assert.deepEqual(value.modifiers, ['reset', 'bold', 'dim', 'italic', 'underline', 'underlineDouble', 'underlineCurly', 'underlineDotted', 'underlineDashed', 'overline', 'inverse', 'hidden', 'strikethrough']);
  assert.deepEqual(value.foreground, ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'blackBright', 'gray', 'grey', 'redBright', 'greenBright', 'yellowBright', 'blueBright', 'magentaBright', 'cyanBright', 'whiteBright']);
  assert.deepEqual(value.background, ['bgBlack', 'bgRed', 'bgGreen', 'bgYellow', 'bgBlue', 'bgMagenta', 'bgCyan', 'bgWhite', 'bgBlackBright', 'bgGray', 'bgGrey', 'bgRedBright', 'bgGreenBright', 'bgYellowBright', 'bgBlueBright', 'bgMagentaBright', 'bgCyanBright', 'bgWhiteBright']);
  assert.deepEqual(value.underline, ['underlineBlack', 'underlineRed', 'underlineGreen', 'underlineYellow', 'underlineBlue', 'underlineMagenta', 'underlineCyan', 'underlineWhite', 'underlineBlackBright', 'underlineGray', 'underlineGrey', 'underlineRedBright', 'underlineGreenBright', 'underlineYellowBright', 'underlineBlueBright', 'underlineMagentaBright', 'underlineCyanBright', 'underlineWhiteBright']);
});

test('colorNames combines foreground and background names', () => {
  const value = inventory();
  assert.deepEqual(value.colors, [...value.foreground, ...value.background]);
});

test('all modifier pairs use the documented ANSI codes', () => {
  const expected = {reset: [0, 0], bold: [1, 22], dim: [2, 22], italic: [3, 23], underline: [4, 24], underlineDouble: ['4:2', 24], underlineCurly: ['4:3', 24], underlineDotted: ['4:4', 24], underlineDashed: ['4:5', 24], overline: [53, 55], inverse: [7, 27], hidden: [8, 28], strikethrough: [9, 29]};
  for (const [name, [open, close]] of Object.entries(expected)) assert.deepEqual(style(name), {open: `${esc}[${open}m`, close: `${esc}[${close}m`});
});

test('basic foreground colors use standard close code', () => {
  for (const [name, code] of Object.entries({black: 30, red: 31, green: 32, yellow: 33, blue: 34, magenta: 35, cyan: 36, white: 37})) assert.deepEqual(style(name), {open: `${esc}[${code}m`, close: `${esc}[39m`});
});

test('bright foreground aliases have the expected pairs', () => {
  for (const [name, code] of Object.entries({blackBright: 90, gray: 90, grey: 90, redBright: 91, greenBright: 92, yellowBright: 93, blueBright: 94, magentaBright: 95, cyanBright: 96, whiteBright: 97})) assert.deepEqual(style(name), {open: `${esc}[${code}m`, close: `${esc}[39m`});
});

test('basic background colors use standard close code', () => {
  for (const [name, code] of Object.entries({bgBlack: 40, bgRed: 41, bgGreen: 42, bgYellow: 43, bgBlue: 44, bgMagenta: 45, bgCyan: 46, bgWhite: 47})) assert.deepEqual(style(name), {open: `${esc}[${code}m`, close: `${esc}[49m`});
});

test('bright background aliases have the expected pairs', () => {
  for (const [name, code] of Object.entries({bgBlackBright: 100, bgGray: 100, bgGrey: 100, bgRedBright: 101, bgGreenBright: 102, bgYellowBright: 103, bgBlueBright: 104, bgMagentaBright: 105, bgCyanBright: 106, bgWhiteBright: 107})) assert.deepEqual(style(name), {open: `${esc}[${code}m`, close: `${esc}[49m`});
});

test('style groups are non-enumerable and expose family names', () => {
  const value = inventory();
  assert.deepEqual(value.groupEnumerable, {modifier: false, color: false, bgColor: false, underlineColor: false, codes: false});
  assert.deepEqual(group('modifier'), {names: value.modifiers});
  assert.equal(group('color').close, `${esc}[39m`);
  assert.equal(group('bgColor').close, `${esc}[49m`);
  assert.equal(group('underlineColor').close, `${esc}[59m`);
});

test('codes is a Map with the standard close mappings', () => {
  const value = inventory();
  const entries = new Map(value.codeEntries);
  assert.equal(entries.get(0), 0);
  assert.equal(entries.get(1), 22);
  assert.equal(entries.get(31), 39);
  assert.equal(entries.get(40), 49);
  assert.equal(entries.get(53), 55);
  assert.equal(entries.get(58), 59);
});

test('style pairs have complete string values', () => {
  const value = inventory();
  for (const name of [...value.modifiers, ...value.foreground, ...value.background, ...value.underline]) {
    const pair = style(name);
    assert.equal(typeof pair.open, 'string');
    assert.equal(typeof pair.close, 'string');
    assert.match(pair.open, /^\u001b\[[0-9;:]+m$/);
    assert.match(pair.close, /^\u001b\[[0-9;]+m$/);
  }
});

test('conversion helpers are non-enumerable implementation details', () => {
  const value = inventory();
  for (const name of ['rgbToAnsi256', 'hexToRgb', 'hexToAnsi256', 'ansi256ToAnsi', 'rgbToAnsi', 'hexToAnsi']) {
    assert.equal(value.enumerableKeys.includes(name), false);
  }
});

test('foreground aliases share the same escape pair', () => {
  assert.deepEqual(style('gray'), style('blackBright'));
  assert.deepEqual(style('grey'), style('blackBright'));
});

test('background aliases share the same escape pair', () => {
  assert.deepEqual(style('bgGray'), style('bgBlackBright'));
  assert.deepEqual(style('bgGrey'), style('bgBlackBright'));
});

test('foreground 16-color builder emits a complete sequence', () => {
  assert.equal(convert('group-ansi', [31]), `${esc}[31m`);
});

test('background 16-color builder adds the background offset', () => {
  assert.equal(convert('bg-ansi', [31]), `${esc}[41m`);
  assert.equal(convert('underline-ansi', [31]), `${esc}[58;5;1m`);
});

test('foreground 256-color builder emits a complete sequence', () => {
  assert.equal(convert('group-ansi256', [196]), `${esc}[38;5;196m`);
  assert.equal(convert('underline-ansi256', [196]), `${esc}[58;5;196m`);
});

test('background 256-color builder emits a complete sequence', () => {
  assert.equal(convert('bg-ansi256', [196]), `${esc}[48;5;196m`);
});

test('foreground truecolor builder emits RGB components', () => {
  assert.equal(convert('group-ansi16m', [1, 2, 3]), `${esc}[38;2;1;2;3m`);
  assert.equal(convert('underline-ansi16m', [1, 2, 3]), `${esc}[58;2;1;2;3m`);
});

test('background truecolor builder emits RGB components', () => {
  assert.equal(convert('bg-ansi16m', [1, 2, 3]), `${esc}[48;2;1;2;3m`);
});

test('rgbToAnsi256 handles the low grayscale boundary', () => {
  assert.equal(convert('rgbToAnsi256', [0, 0, 0]), 16);
  assert.equal(convert('rgbToAnsi256', [7, 7, 7]), 16);
});

test('rgbToAnsi256 handles the high grayscale boundary', () => {
  assert.equal(convert('rgbToAnsi256', [249, 249, 249]), 231);
  assert.equal(convert('rgbToAnsi256', [255, 255, 255]), 231);
});

test('rgbToAnsi256 maps a middle grayscale value', () => {
  assert.equal(convert('rgbToAnsi256', [128, 128, 128]), 244);
});

test('rgbToAnsi256 maps primary colors into the color cube', () => {
  assert.equal(convert('rgbToAnsi256', [255, 0, 0]), 196);
  assert.equal(convert('rgbToAnsi256', [0, 255, 0]), 46);
  assert.equal(convert('rgbToAnsi256', [0, 0, 255]), 21);
});

test('hexToRgb expands six-digit input', () => {
  assert.deepEqual(convert('hexToRgb', ['#abcdef']), [171, 205, 239]);
});

test('hexToRgb expands three-digit input', () => {
  assert.deepEqual(convert('hexToRgb', ['#abc']), [170, 187, 204]);
});

test('hexToRgb returns black for invalid input', () => {
  assert.deepEqual(convert('hexToRgb', ['not-a-color']), [0, 0, 0]);
});

test('hexToRgb accepts numeric RGB values', () => {
  assert.deepEqual(convert('hexToRgb', [0xabcdef]), [171, 205, 239]);
});

test('hexToAnsi256 agrees with RGB conversion', () => {
  assert.equal(convert('hexToAnsi256', ['#ff0000']), 196);
  assert.equal(convert('hexToAnsi256', ['#808080']), 244);
});

test('ansi256ToAnsi handles normal and bright base colors', () => {
  assert.equal(convert('ansi256ToAnsi', [0]), 30);
  assert.equal(convert('ansi256ToAnsi', [7]), 37);
  assert.equal(convert('ansi256ToAnsi', [8]), 90);
  assert.equal(convert('ansi256ToAnsi', [15]), 97);
});

test('ansi256ToAnsi reduces extended colors deterministically', () => {
  assert.equal(convert('ansi256ToAnsi', [196]), 91);
  assert.equal(convert('ansi256ToAnsi', [244]), 37);
});

test('RGB and hex 16-color helpers agree with ANSI reduction', () => {
  assert.equal(convert('rgbToAnsi', [255, 0, 0]), 91);
  assert.equal(convert('hexToAnsi', ['#ff0000']), 91);
  assert.equal(convert('hexToAnsi', ['#808080']), 37);
});
