import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call, error, parse, parseHelp} from './test_client.mjs';

test('root default export returns the documented result shape', () => {
	const result = parse(['hello'], {flags: {loud: {type: 'boolean'}}});
	assert.deepEqual(Object.keys(result).sort(), ['flags', 'help', 'input', 'pkg', 'unnormalizedFlags'].sort());
	assert.deepEqual(result.input, ['hello']);
	assert.equal(typeof result.flags, 'object');
	assert.equal(typeof result.pkg, 'object');
});

test('positional string input is preserved', () => assert.deepEqual(parse(['hello']).input, ['hello']));
test('multiple positional inputs are preserved in order', () => assert.deepEqual(parse(['a', 'b']).input, ['a', 'b']));
test('number input converts a positional value', () => assert.deepEqual(parse(['7'], {input: 'number'}).input, [7]));
test('boolean input keeps positional strings', () => assert.deepEqual(parse(['true'], {input: 'boolean'}).input, ['true']));
test('array input returns positional values as an array', () => assert.deepEqual(parse(['a', 'b'], {input: 'array'}).input, ['a', 'b']));
test('inferType converts numeric positional values', () => assert.deepEqual(parse(['7'], {inferType: true}).input, [7]));
test('string flags consume their following value', () => assert.equal(parse(['--name', 'Ada'], {flags: {name: {type: 'string'}}}).flags.name, 'Ada'));
test('equals syntax is supported for flags', () => assert.equal(parse(['--name=Ada'], {flags: {name: {type: 'string'}}}).flags.name, 'Ada'));
test('boolean flags default to false', () => assert.equal(parse([], {flags: {verbose: {type: 'boolean'}}}).flags.verbose, false));
test('boolean flags become true when present', () => assert.equal(parse(['--verbose'], {flags: {verbose: {type: 'boolean'}}}).flags.verbose, true));
test('boolean flags support no negation', () => assert.equal(parse(['--no-verbose'], {flags: {verbose: {type: 'boolean', default: true}}}).flags.verbose, false));
test('number flags convert numeric values', () => assert.equal(parse(['--count', '4'], {flags: {count: {type: 'number'}}}).flags.count, 4));
test('flag defaults are returned when absent', () => assert.equal(parse([], {flags: {name: {type: 'string', default: 'Ada'}}}).flags.name, 'Ada'));
test('short flags are accepted', () => assert.equal(parse(['-v'], {flags: {verbose: {type: 'boolean', shortFlag: 'v'}}}).flags.verbose, true));
test('grouped short boolean flags are accepted', () => assert.deepEqual(parse(['-abc'], {flags: {a: {type: 'boolean'}, b: {type: 'boolean'}, c: {type: 'boolean'}}}).flags, {a: true, b: true, c: true}));
test('aliases populate the unnormalized result', () => {
	const result = parse(['--colour', 'red'], {flags: {color: {type: 'string', aliases: ['colour']}}});
	assert.equal(result.flags.color, 'red');
	assert.equal(result.unnormalizedFlags.colour, 'red');
});
test('camel-case flag keys accept kebab-case arguments', () => assert.equal(parse(['--dry-run'], {flags: {dryRun: {type: 'boolean'}}}).flags.dryRun, true));
test('multiple flags return an array', () => assert.deepEqual(parse(['--tag', 'a', '--tag', 'b'], {flags: {tag: {type: 'string', isMultiple: true}}}).flags.tag, ['a', 'b']));
test('multiple flags default to an empty array', () => assert.deepEqual(parse([], {flags: {tag: {type: 'string', isMultiple: true}}}).flags.tag, []));
test('multiple boolean flags return boolean values', () => assert.deepEqual(parse(['--feature', '--no-feature'], {flags: {feature: {type: 'boolean', isMultiple: true}}}).flags.feature, [true, false]));
test('choices accept a declared value', () => assert.equal(parse(['--color', 'red'], {flags: {color: {type: 'string', choices: ['red', 'blue']}}}).flags.color, 'red'));
test('choices reject an undeclared value', () => assert.match(error(['--color', 'green'], {flags: {color: {type: 'string', choices: ['red', 'blue']}}}), /Unknown value/));
test('unknown flags are accepted by default', () => assert.equal(parse(['--other', 'x']).flags.other, 'x'));
test('unknown flags fail closed when rejection exits the child', () => assert.match(error(['--other'], {allowUnknownFlags: false}), /candidate-call-failed|malformed/));
test('required input fails closed when validation exits the child', () => assert.match(error([], {input: {type: 'string', isRequired: true}}), /candidate-call-failed|malformed/));
test('commands return the first positional token', () => {
	const result = parse(['run', '--verbose'], {commands: ['run', 'list'], flags: {verbose: {type: 'boolean'}}});
	assert.equal(result.command, 'run');
	assert.deepEqual(result.input, ['--verbose']);
});
test('commands accept a trailing command input', () => assert.deepEqual(parse(['list', 'file.txt'], {commands: ['run', 'list']}).input, ['file.txt']));
test('unknown commands fail closed when validation exits the child', () => assert.match(error(['remove'], {commands: ['run', 'list']}), /candidate-call-failed|malformed/));
test('description is included in help', () => assert.match(parseHelp('Usage\n  $ demo', []).help, /Demo description/));
test('description can be disabled', () => assert.doesNotMatch(parseHelp('Usage\n  $ demo', [], {description: false}).help, /Demo description/));
test('help text is trimmed and starts with a newline', () => assert.equal(parseHelp('\n  Usage\n    $ demo\n', []).help, '\n  Demo description\n\n  Usage\n    $ demo\n'));
test('help indentation is configurable', () => assert.equal(parseHelp('\nUsage\n  $ demo\n', [], {helpIndent: 4}).help, '\n    Demo description\n\n    Usage\n      $ demo\n'));
test('custom package metadata is returned', () => assert.equal(parse([], {pkg: {name: 'custom', version: '1.0.0'}}).pkg.name, 'custom'));
test('options-only invocation is supported', () => assert.deepEqual(parse([], {flags: {quiet: {type: 'boolean'}}}).input, []));
test('default description comes from package metadata', () => assert.match(parse([], {}).help, /Demo description/));
test('default version is read from package metadata', () => assert.equal(parse([], {}).pkg.version, '3.2.1'));
