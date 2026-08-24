import assert from 'node:assert/strict';
import {mkdtemp, rm, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {test} from 'node:test';
import {call} from './test_client.mjs';

const node = process.execPath;
const script = code => ['-e', code];
const run = (name, args, options) => call(name, [node, args, options].filter(value => value !== undefined));

test('package-exports', () => {
	assert.deepEqual(call('parseCommandString', ['node a\\ b']), ['node', 'a b']);
	assert.equal(typeof call('execa', [node, script('process.stdout.write("ok")')]).stdout, 'string');
});

test('async-success', () => {
	const result = run('execa', script('process.stdout.write("hello\\n"); process.stderr.write("warn\\n")'));
	assert.equal(result.stdout, 'hello');
	assert.equal(result.stderr, 'warn');
	assert.equal(result.exitCode, 0);
	assert.equal(result.failed, false);
});

test('argument-boundaries', () => {
	const result = run('execa', script('process.stdout.write(process.argv[1])').concat(['a b; echo forged']));
	assert.equal(result.stdout, 'a b; echo forged');
});

test('input-and-newline', () => {
	const code = 'let value=""; process.stdin.on("data", chunk => value += chunk); process.stdin.on("end", () => process.stdout.write(value + "\\n"))';
	assert.equal(run('execa', script(code), {input: 'alpha'}).stdout, 'alpha');
	assert.equal(run('execa', script(code), {input: 'alpha', stripFinalNewline: false}).stdout, 'alpha\n');
});

test('environment-and-cwd', async () => {
	const dir = await mkdtemp(join(tmpdir(), 'execa-test-'));
	try {
		const code = 'process.stdout.write(`${process.cwd()}|${process.env.EXECA_MARK}|${process.env.PATH ? "path" : "no-path"}`)';
		const result = run('execa', script(code), {cwd: dir, env: {EXECA_MARK: 'yes'}});
		assert.equal(result.stdout, `${dir}|yes|path`);
		assert.equal(run('execa', script('process.stdout.write(process.env.EXECA_MARK ?? "missing")'), {extendEnv: false, env: {EXECA_MARK: 'isolated'}}).stdout, 'isolated');
	} finally {
		await rm(dir, {recursive: true, force: true});
	}
});

test('async-failure', () => {
	assert.throws(() => run('execa', script('process.stderr.write("bad"); process.exit(3)')), /exit code 3/);
});

test('reject-false', () => {
	const result = run('execa', script('process.stderr.write("bad"); process.exit(2)'), {reject: false});
	assert.equal(result.exitCode, 2);
	assert.equal(result.stderr, 'bad');
	assert.equal(result.failed, true);
});

test('sync-execution', () => {
	const result = run('execaSync', script('process.stdout.write("sync\\n")'));
	assert.equal(result.stdout, 'sync');
	assert.equal(result.exitCode, 0);
	assert.equal(run('execaSync', script('process.exit(4)'), {reject: false}).exitCode, 4);
});

test('node-execution', async () => {
	const dir = await mkdtemp(join(tmpdir(), 'execa-node-'));
	const file = join(dir, 'child.mjs');
	try {
		await writeFile(file, 'process.stdout.write(process.argv.slice(2).join("|"));\n');
		assert.equal(call('execaNode', [file, ['one', 'two words']]).stdout, 'one|two words');
	} finally {
		await rm(dir, {recursive: true, force: true});
	}
});

test('parse-command', () => {
	assert.deepEqual(call('parseCommandString', ['node "a b"']), ['node', '"a', 'b"']);
});

test('timeout', () => {
	const result = run('execa', script('setTimeout(() => {}, 5000)'), {timeout: 50, reject: false});
	assert.equal(result.timedOut, true);
	assert.equal(result.failed, true);
});
