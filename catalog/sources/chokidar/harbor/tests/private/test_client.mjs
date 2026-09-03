import {appendFile, mkdtemp, mkdir, readFile, rm, unlink, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, relative} from 'node:path';
import {pathToFileURL} from 'node:url';
const site = process.env.NODE_CANDIDATE_SITE;
if (!site) throw new Error('candidate site is not configured');

const packageRoot = join(site, 'node_modules', 'chokidar');
const packageJson = JSON.parse(await readFile(join(packageRoot, 'package.json'), 'utf8'));
const entry = packageJson.exports?.['.']?.default ?? packageJson.main;
if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) {
  throw new Error('candidate has no safe package entry');
}
const api = await import(pathToFileURL(join(packageRoot, entry)).href);

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const rel = (root, path) => relative(root, path) || '.';

async function fixture(fn) {
  const root = await mkdtemp(join(tmpdir(), 'chokidar-contract-'));
  try {
    return await fn(root);
  } finally {
    await rm(root, {recursive: true, force: true});
  }
}

function waitFor(watcher, event, root, expectedPath, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      watcher.off(event, onEvent);
      reject(new Error(`timed out waiting for ${event}`));
    }, timeout);
    const onEvent = (path) => {
      if (expectedPath && path !== expectedPath) return;
      clearTimeout(timer);
      watcher.off(event, onEvent);
      resolve(rel(root, path));
    };
    watcher.on(event, onEvent);
  });
}

async function ready(watcher) {
  if (watcher._readyEmitted) return;
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('timed out waiting for ready')), 5000);
    watcher.once('ready', () => {
      clearTimeout(timer);
      resolve();
    });
    watcher.once('error', reject);
  });
}

async function initialTree(options = {}) {
  return fixture(async (root) => {
    await mkdir(join(root, 'sub', 'deep'), {recursive: true});
    await writeFile(join(root, 'top.txt'), 'top');
    await writeFile(join(root, 'sub', 'nested.txt'), 'nested');
    await writeFile(join(root, 'sub', 'deep', 'deep.txt'), 'deep');
    const watcher = api.watch(root, options);
    const events = [];
    watcher.on('all', (event, path) => events.push(`${event}:${rel(root, path)}`));
    await ready(watcher);
    await watcher.close();
    return {events: events.sort()};
  });
}

async function mutate(kind, options = {}) {
  return fixture(async (root) => {
    const target = join(root, 'item.txt');
    if (kind === 'change' || kind === 'unlink') await writeFile(target, 'before');
    const watcher = api.watch(root, {
      ...options,
      ...(kind === 'change' ? {usePolling: true, interval: 10} : {}),
      ignoreInitial: true,
    });
    const events = [];
    watcher.on('all', (event, path) => events.push(`${event}:${rel(root, path)}`));
    await ready(watcher);
    if (kind === 'add') {
      await writeFile(target, 'new');
      await waitFor(watcher, 'add', root, target);
    } else if (kind === 'change') {
      await delay(1000);
      await appendFile(target, ' after with a different size');
      await waitFor(watcher, 'change', root, target);
    } else {
      await unlink(target);
      await waitFor(watcher, 'unlink', root, target);
    }
    await watcher.close();
    return {events};
  });
}

async function scenario(operation, args = {}) {
  if (operation === 'inventory') {
    return {
      packageName: packageJson.name,
      packageVersion: packageJson.version,
      type: packageJson.type,
      hasMain: typeof packageJson.main === 'string',
      hasDeclaration: (await readFile(join(packageRoot, 'index.d.ts'), 'utf8')).length > 0,
      defaultKeys: Object.keys(api.default).sort(),
      hasWatch: typeof api.watch === 'function',
      hasFSWatcher: typeof api.FSWatcher === 'function',
    };
  }
  if (operation === 'initial') return initialTree(args);
  if (operation === 'add') return mutate('add', args);
  if (operation === 'change') return mutate('change', args);
  if (operation === 'unlink') return mutate('unlink', args);
  if (operation === 'polling-change') return mutate('change', {usePolling: true, interval: 10});
  if (operation === 'ignored') {
    return fixture(async (root) => {
      await writeFile(join(root, 'keep.txt'), 'keep');
      await writeFile(join(root, 'skip.txt'), 'skip');
      const watcher = api.watch(root, {ignored: join(root, 'skip.txt')});
      const events = [];
      watcher.on('all', (event, path) => events.push(`${event}:${rel(root, path)}`));
      await ready(watcher);
      await watcher.close();
      return {events: events.sort()};
    });
  }
  if (operation === 'cwd') {
    return fixture(async (root) => {
      await writeFile(join(root, 'keep.txt'), 'keep');
      const watcher = api.watch(root, {cwd: root});
      const events = [];
      watcher.on('all', (event, path) => events.push(`${event}:${path}`));
      await ready(watcher);
      const watched = watcher.getWatched();
      await watcher.close();
      return {events: events.sort(), watchedKeys: Object.keys(watched).sort()};
    });
  }
  if (operation === 'depth') return initialTree({depth: 0});
  if (operation === 'get-watched') {
    return fixture(async (root) => {
      await mkdir(join(root, 'sub'));
      await writeFile(join(root, 'top.txt'), 'top');
      await writeFile(join(root, 'sub', 'nested.txt'), 'nested');
      const watcher = api.watch(root);
      await ready(watcher);
      const watched = watcher.getWatched();
      await watcher.close();
      return Object.fromEntries(Object.entries(watched).map(([key, value]) => [rel(root, key), value]));
    });
  }
  if (operation === 'dynamic') {
    return fixture(async (root) => {
      const target = join(root, 'dynamic.txt');
      await writeFile(target, 'before');
      const watcher = new api.FSWatcher({ignoreInitial: true, usePolling: true, interval: 10});
      const events = [];
      watcher.on('all', (event, path) => events.push(`${event}:${rel(root, path)}`));
      const returned = watcher.add(target);
      await ready(watcher);
      await delay(1000);
      await appendFile(target, ' after with a different size');
      await waitFor(watcher, 'change', root, target);
      const same = returned === watcher;
      watcher.unwatch(target);
      await writeFile(target, 'after-again');
      await delay(150);
      await watcher.close();
      return {same, changeCount: events.filter((event) => event === 'change:dynamic.txt').length};
    });
  }
  if (operation === 'close') {
    return fixture(async (root) => {
      const watcher = api.watch(root, {ignoreInitial: true});
      const events = [];
      watcher.on('all', (event, path) => events.push(`${event}:${rel(root, path)}`));
      await ready(watcher);
      const first = watcher.close();
      const second = watcher.close();
      await Promise.all([first, second]);
      await writeFile(join(root, 'after-close.txt'), 'after');
      await delay(100);
      return {closed: watcher.closed, samePromise: first === second, events};
    });
  }
  if (operation === 'invalid-path') {
    try {
      api.watch(42);
      return {threw: false};
    } catch (error) {
      return {threw: true, name: error.name, message: error.message};
    }
  }
  throw new Error('operation is not allowlisted');
}

const request = JSON.parse(await new Promise((resolve, reject) => {
  let data = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (chunk) => { data += chunk; });
  process.stdin.on('end', () => resolve(data));
  process.stdin.on('error', reject);
}));
try {
  const value = await scenario(request.operation, request.args ?? {});
  process.stdout.write(JSON.stringify({ok: true, value}) + '\n');
} catch (error) {
  process.stdout.write(JSON.stringify({ok: false, message: String(error?.message ?? error)}) + '\n');
  process.exitCode = 1;
}


