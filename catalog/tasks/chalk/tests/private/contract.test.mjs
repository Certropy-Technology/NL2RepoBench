import assert from 'node:assert/strict';
import {test} from 'node:test';
import {format, inventory, levelAssignment, levelTransition} from './test_client.mjs';

const esc = '\u001B';
const step = (name, ...args) => ({name, args});

test('package root exposes callable Chalk values and aliases', () => {
	const value = inventory();
	assert.equal(value.defaultCallable, true);
	assert.equal(value.packageShape, true);
	assert.equal(value.chalkConstructor, true);
	assert.equal(value.chalkStderrCallable, true);
	assert.deepEqual(value.aliases, {
		modifiers: true,
		foregroundColors: true,
		backgroundColors: true,
		colors: true,
	});
});

test('level zero returns unstyled text', () => {
	assert.equal(format(0, [step('red')], ['plain']), 'plain');
});

test('basic foreground color wraps text', () => {
	assert.equal(format(1, [step('red')], ['plain']), `${esc}[31mplain${esc}[39m`);
});

test('named modifiers and grey alias use their ANSI sequences', () => {
	assert.equal(format(1, [step('underlineCurly')], ['x']), `${esc}[4:3mx${esc}[24m`);
	assert.equal(format(1, [step('grey')], ['x']), `${esc}[90mx${esc}[39m`);
});

test('background and underline colors close their own families', () => {
	assert.equal(
		format(1, [step('bgBlue'), step('underlineRed')], ['x']),
		`${esc}[44m${esc}[58;5;1mx${esc}[59m${esc}[49m`,
	);
});

test('chains open in order and close in reverse order', () => {
	assert.equal(
		format(1, [step('red'), step('bold'), step('underline')], ['x']),
		`${esc}[31m${esc}[1m${esc}[4mx${esc}[24m${esc}[22m${esc}[39m`,
	);
});

test('an existing close sequence reopens the outer style', () => {
	assert.equal(
		format(1, [step('red')], [`a${esc}[32mb${esc}[39mc`]),
		`${esc}[31ma${esc}[32mb${esc}[39m${esc}[31mc${esc}[39m`,
	);
});

test('line feed closes and reopens an active style', () => {
	assert.equal(
		format(1, [step('red')], ['a\nb']),
		`${esc}[31ma${esc}[39m\n${esc}[31mb${esc}[39m`,
	);
});

test('CRLF remains CRLF while an active style is reopened', () => {
	assert.equal(
		format(1, [step('red')], ['a\r\nb']),
		`${esc}[31ma${esc}[39m\r\n${esc}[31mb${esc}[39m`,
	);
});

test('empty styled text does not emit escape codes', () => {
	assert.equal(format(3, [step('red'), step('bold')], []), '');
});

test('visible suppresses text at level zero', () => {
	assert.equal(format(0, [step('visible'), step('red')], ['x']), '');
});

test('visible preserves adjacent styles at a positive level', () => {
	assert.equal(format(1, [step('visible'), step('red')], ['x']), `${esc}[31mx${esc}[39m`);
});

test('RGB emits truecolor at level three', () => {
	assert.equal(
		format(3, [step('rgb', 255, 0, 0)], ['x']),
		`${esc}[38;2;255;0;0mx${esc}[39m`,
	);
});

test('hex emits truecolor at level three', () => {
	assert.equal(
		format(3, [step('hex', '#00ff00')], ['x']),
		`${esc}[38;2;0;255;0mx${esc}[39m`,
	);
});

test('ANSI 256 stays ANSI 256 at levels two and three', () => {
	for (const level of [2, 3]) {
		assert.equal(format(level, [step('ansi256', 196)], ['x']), `${esc}[38;5;196mx${esc}[39m`);
	}
});

test('RGB downsampling uses basic bright red at level one', () => {
	assert.equal(format(1, [step('rgb', 255, 0, 0)], ['x']), `${esc}[91mx${esc}[39m`);
});

test('background and underline RGB models use level-three families', () => {
	assert.equal(
		format(3, [step('bgRgb', 1, 2, 3)], ['x']),
		`${esc}[48;2;1;2;3mx${esc}[49m`,
	);
	assert.equal(
		format(3, [step('underlineRgb', 1, 2, 3)], ['x']),
		`${esc}[58;2;1;2;3mx${esc}[59m`,
	);
	assert.equal(format(3, [step('bgHex', '#010203')], ['x']), `${esc}[48;2;1;2;3mx${esc}[49m`);
	assert.equal(format(2, [step('bgAnsi256', 196)], ['x']), `${esc}[48;5;196mx${esc}[49m`);
	assert.equal(format(2, [step('underlineAnsi256', 196)], ['x']), `${esc}[58;5;196mx${esc}[59m`);
});

test('color models are disabled at level zero', () => {
	assert.equal(format(0, [step('underlineHex', '#ff0000')], ['x']), 'x');
});

test('JSON values use ordinary join coercion', () => {
	assert.equal(
		format(1, [step('bold')], ['hello', 42, true, null, ['a', 'b'], {key: 'value'}]),
		`${esc}[1mhello 42 true  a,b [object Object]${esc}[22m`,
	);
});

test('derived builders share the root level', () => {
	assert.deepEqual(
		levelTransition({start: 1, next: 0, chain: [step('red')], values: ['x']}),
		{rootLevel: 0, builderLevel: 0, value: 'x'},
	);
});

test('an invalid construction level raises an ordinary Error', () => {
	assert.throws(() => format(4, [step('red')], ['x']), /integer from 0 to 3/);
});

test('an invalid builder level leaves the old root level intact', () => {
	const value = levelAssignment({start: 1, next: 4, chain: [step('red')], values: ['x']});
	assert.equal(value.rootLevel, 1);
	assert.equal(value.builderLevel, 1);
	assert.match(value.error, /integer from 0 to 3/);
	assert.equal(value.value, `${esc}[31mx${esc}[39m`);
});

test('all documented name arrays are exported', () => {
	const value = inventory();
	assert.deepEqual(value.modifierNames, [
		'reset', 'bold', 'dim', 'italic', 'underline', 'underlineDouble', 'underlineCurly',
		'underlineDotted', 'underlineDashed', 'overline', 'inverse', 'hidden', 'strikethrough',
	]);
	assert.deepEqual(value.foregroundColorNames, [
		'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'blackBright',
		'gray', 'grey', 'redBright', 'greenBright', 'yellowBright', 'blueBright',
		'magentaBright', 'cyanBright', 'whiteBright',
	]);
	assert.deepEqual(value.backgroundColorNames, [
		'bgBlack', 'bgRed', 'bgGreen', 'bgYellow', 'bgBlue', 'bgMagenta', 'bgCyan', 'bgWhite',
		'bgBlackBright', 'bgGray', 'bgGrey', 'bgRedBright', 'bgGreenBright', 'bgYellowBright',
		'bgBlueBright', 'bgMagentaBright', 'bgCyanBright', 'bgWhiteBright',
	]);
	assert.deepEqual(value.underlineColorNames, [
		'underlineBlack', 'underlineRed', 'underlineGreen', 'underlineYellow', 'underlineBlue',
		'underlineMagenta', 'underlineCyan', 'underlineWhite', 'underlineBlackBright',
		'underlineGray', 'underlineGrey', 'underlineRedBright', 'underlineGreenBright',
		'underlineYellowBright', 'underlineBlueBright', 'underlineMagentaBright',
		'underlineCyanBright', 'underlineWhiteBright',
	]);
	assert.equal(value.colorNames.includes('underlineRed'), false);
	for (const name of [
		...value.modifierNames, ...value.foregroundColorNames,
		...value.backgroundColorNames, ...value.underlineColorNames,
	]) assert.equal(typeof format(1, [step(name)], ['x']), 'string', name);
});

test('deterministic pipe environment reports no color support', () => {
	const value = inventory();
	assert.equal(value.supportsColor, false);
	assert.equal(value.supportsColorStderr, false);
});
