import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdirSync} from 'node:fs';
import {test} from 'node:test';
import {join} from 'node:path';

const runner = join(import.meta.dirname, 'test_client.mjs');
function call(operation, args = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  mkdirSync(join(site, 'tmp'), {recursive: true});
  mkdirSync(join(site, 'home'), {recursive: true});
  const result = spawnSync(process.execPath, ['--no-addons', '--no-warnings', runner], {
    input: JSON.stringify({operation, args}) + '\n',
    encoding: 'utf8',
    timeout: 15000,
    maxBuffer: 256 * 1024,
    env: {PATH: '/usr/local/bin:/usr/bin:/bin', HOME: join(site, 'home'), TMPDIR: join(site, 'tmp'), NODE_CANDIDATE_SITE: site, LC_ALL: 'C.UTF-8'},
  });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(String(result.stderr || result.stdout));
  const response = JSON.parse(result.stdout);
  if (!response.ok) throw new Error(response.message);
  return response.value;
}
const inventory = () => call('inventory');
const scenario = (operation, args = {}) => call(operation, args);

const eventNames = (value) => value.events.map((event) => event.split(':', 1)[0]);

test('package metadata exposes the ESM root and declarations', async () => {
  assert.deepEqual(await inventory(), {
    packageName: 'chokidar', packageVersion: '5.0.0', type: 'module', hasMain: true,
    hasDeclaration: true, defaultKeys: ['FSWatcher', 'watch'], hasWatch: true, hasFSWatcher: true,
  });
});

test('initial scan reports directories and files', async () => {
  const value = await scenario('initial');
  assert.deepEqual(value.events, [
    'add:sub/deep/deep.txt', 'add:sub/nested.txt', 'add:top.txt',
    'addDir:.', 'addDir:sub', 'addDir:sub/deep',
  ]);
});

test('initial scan can suppress initial events', async () => {
  const value = await scenario('initial', {ignoreInitial: true});
  assert.deepEqual(value.events, []);
});

test('new files emit add and all events', async () => {
  const value = await scenario('add');
  assert.deepEqual(value.events, ['add:item.txt']);
});

test('changed files emit change and all events', async () => {
  const value = await scenario('change');
  assert.deepEqual(value.events, ['change:item.txt']);
});

test('removed files emit unlink and all events', async () => {
  const value = await scenario('unlink');
  assert.deepEqual(value.events, ['unlink:item.txt']);
});

test('polling backend reports changes', async () => {
  const value = await scenario('polling-change');
  assert.deepEqual(value.events, ['change:item.txt']);
});

test('ignored paths are absent from initial scan', async () => {
  const value = await scenario('ignored');
  assert.deepEqual(value.events, ['add:keep.txt', 'addDir:.']);
});

test('cwd makes emitted paths relative', async () => {
  const value = await scenario('cwd');
  assert.deepEqual(value.events, ['add:keep.txt', 'addDir:']);
  assert.equal(value.watchedKeys.includes('.'), true);
  assert.equal(value.watchedKeys.every((key) => !key.startsWith('/')), true);
});

test('depth zero does not traverse nested directories', async () => {
  const value = await scenario('depth');
  assert.deepEqual(value.events, ['add:top.txt', 'addDir:.', 'addDir:sub']);
});

test('getWatched returns directory names and sorted children', async () => {
  const value = await scenario('get-watched');
  assert.deepEqual(value['.'], ['sub', 'top.txt']);
  assert.deepEqual(value.sub, ['nested.txt']);
});

test('dynamic add is chainable and watches the path', async () => {
  const value = await scenario('dynamic');
  assert.equal(value.same, true);
  assert.equal(value.changeCount, 1);
});

test('close is idempotent and stops further events', async () => {
  const value = await scenario('close');
  assert.deepEqual(value, {closed: true, samePromise: true, events: []});
});

test('invalid watch paths fail synchronously', async () => {
  const value = await scenario('invalid-path');
  assert.equal(value.threw, true);
  assert.equal(value.name, 'TypeError');
});

test('event observations contain only documented event names', async () => {
  const value = await scenario('initial');
  assert.deepEqual([...new Set(eventNames(value))].sort(), ['add', 'addDir']);
});

test('initial files preserve relative hierarchy', async () => {
  const value = await scenario('initial');
  assert.ok(value.events.includes('add:sub/deep/deep.txt'));
  assert.ok(value.events.includes('add:sub/nested.txt'));
});

test('initial directory events include the root', async () => {
  const value = await scenario('initial');
  assert.ok(value.events.includes('addDir:.'));
});

test('watch returns an FSWatcher instance with methods', async () => {
  const value = await inventory();
  assert.deepEqual(value.defaultKeys, ['FSWatcher', 'watch']);
  assert.equal(value.hasFSWatcher, true);
});

test('watching a file does not require a directory API in the contract', async () => {
  const value = await scenario('change');
  assert.equal(value.events[0].startsWith('change:'), true);
});

test('polling and fs.watch use the same normalized event name', async () => {
  const value = await scenario('polling-change');
  assert.equal(value.events[0].split(':')[0], 'change');
});

test('ignored file does not produce addDir for its name', async () => {
  const value = await scenario('ignored');
  assert.equal(value.events.some((event) => event.includes('skip.txt')), false);
});

test('cwd watched output is relative to the configured directory', async () => {
  const value = await scenario('cwd');
  assert.equal(value.watchedKeys.includes('.'), true);
});

test('depth option still watches the root directory', async () => {
  const value = await scenario('depth');
  assert.equal(value.events.includes('addDir:.'), true);
});

test('getWatched children are sorted', async () => {
  const value = await scenario('get-watched');
  assert.deepEqual(value['.'], [...value['.']].sort());
  assert.deepEqual(value.sub, [...value.sub].sort());
});

test('unwatch removes a dynamic path', async () => {
  const value = await scenario('dynamic');
  assert.equal(value.changeCount, 1);
});

test('close marks the watcher closed', async () => {
  const value = await scenario('close');
  assert.equal(value.closed, true);
});

test('close returns the same promise when called twice', async () => {
  const value = await scenario('close');
  assert.equal(value.samePromise, true);
});

test('invalid path error identifies the type contract', async () => {
  const value = await scenario('invalid-path');
  assert.match(value.message, /string/i);
});

test('root export default is the documented object', async () => {
  const value = await inventory();
  assert.deepEqual(value.defaultKeys, ['FSWatcher', 'watch']);
});

