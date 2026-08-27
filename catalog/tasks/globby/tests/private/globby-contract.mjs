import assert from 'node:assert/strict';
import {chmodSync, mkdtempSync, mkdirSync, rmSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import test from 'node:test';
import {callCandidate} from './test_client.mjs';

function fixture() {
	const cwd = mkdtempSync(join(tmpdir(), 'globby-contract-'));
	chmodSync(cwd, 0o755);
	mkdirSync(join(cwd, 'src', 'nested'), {recursive: true});
	writeFileSync(join(cwd, 'root.js'), 'root');
	writeFileSync(join(cwd, 'root.json'), '{}');
	writeFileSync(join(cwd, '.hidden.js'), 'hidden');
	writeFileSync(join(cwd, '.ignore'), 'root.json\nsrc/b.txt\n');
	writeFileSync(join(cwd, 'src', 'a.js'), 'a');
	writeFileSync(join(cwd, 'src', 'b.txt'), 'b');
	writeFileSync(join(cwd, 'src', 'nested', 'c.js'), 'c');
	return cwd;
}

function sorted(value) {
	return [...value].sort();
}

test('globby matches positive patterns and applies negation', async () => {
	const cwd = fixture();
	try {
		const result = await callCandidate('globby', [['**/*.js', '!**/nested/**'], {cwd, dot: true}]);
		assert.deepEqual(sorted(result), ['.hidden.js', 'root.js', 'src/a.js']);
	} finally {
		rmSync(cwd, {recursive: true, force: true});
	}
});

test('globby expands directories by default and can return the directory itself', async () => {
	const cwd = fixture();
	try {
		const expanded = await callCandidate('globby', ['src', {cwd}]);
		assert.deepEqual(sorted(expanded), ['src/a.js', 'src/b.txt', 'src/nested/c.js']);
		const unexpanded = await callCandidate('globby', ['src', {cwd, expandDirectories: false, onlyFiles: false}]);
		assert.deepEqual(unexpanded, ['src']);
	} finally {
		rmSync(cwd, {recursive: true, force: true});
	}
});

test('negation-only patterns expand to a catch-all unless disabled', async () => {
	const cwd = fixture();
	try {
		const expanded = await callCandidate('globby', [['!**/*.json'], {cwd, dot: true}]);
		assert.deepEqual(sorted(expanded), ['.hidden.js', '.ignore', 'root.js', 'src/a.js', 'src/b.txt', 'src/nested/c.js']);
		const disabled = await callCandidate('globby', [['!**/*.json'], {cwd, expandNegationOnlyPatterns: false}]);
		assert.deepEqual(disabled, []);
	} finally {
		rmSync(cwd, {recursive: true, force: true});
	}
});

test('globbySync returns the same deterministic paths as globby', () => {
	const cwd = fixture();
	try {
		const result = callCandidate('globbySync', [['src/**/*.js'], {cwd}]);
		assert.deepEqual(result, ['src/a.js', 'src/nested/c.js']);
	} finally {
		rmSync(cwd, {recursive: true, force: true});
	}
});

test('generateGlobTasks exposes normalized async tasks', async () => {
	const cwd = fixture();
	try {
		const tasks = await callCandidate('generateGlobTasks', [['src/**/*.js', '!src/**/c.js'], {cwd}]);
		assert.equal(tasks.length, 1);
		assert.deepEqual(tasks.map(task => task.patterns), [['src/**/*.js']]);
		assert.ok(tasks[0].options.ignore.includes('src/**/c.js'));
	} finally {
		rmSync(cwd, {recursive: true, force: true});
	}
});

test('generateGlobTasksSync mirrors task normalization', () => {
	const cwd = fixture();
	try {
		const tasks = callCandidate('generateGlobTasksSync', [['src/**/*.js', '!src/**/c.js'], {cwd}]);
		assert.equal(tasks.length, 1);
		assert.ok(tasks[0].options.ignore.includes('src/**/c.js'));
	} finally {
		rmSync(cwd, {recursive: true, force: true});
	}
});

test('isDynamicPattern distinguishes glob syntax from literal paths', () => {
	assert.equal(callCandidate('isDynamicPattern', [['src/**/*.js']]), true);
	assert.equal(callCandidate('isDynamicPattern', [['README.md']]), false);
});

test('convertPathToPattern escapes glob metacharacters', () => {
	const pattern = callCandidate('convertPathToPattern', ['literal [name] (copy).js']);
	assert.match(pattern, /\\\[name\\\]/);
	assert.match(pattern, /\\\(copy\\\)/);
});

test('ignoreFiles applies compatible ignore syntax to results', async () => {
	const cwd = fixture();
	try {
		const result = await callCandidate('globby', [['**/*'], {cwd, dot: true, ignoreFiles: '.ignore'}]);
		assert.deepEqual(sorted(result), ['.hidden.js', '.ignore', 'root.js', 'src/a.js', 'src/nested/c.js']);
	} finally {
		rmSync(cwd, {recursive: true, force: true});
	}
});

test('invalid pattern input fails at the public boundary', () => {
	assert.throws(() => callCandidate('globbySync', [[42]]), /candidate-call-failed/);
});
