import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';
import { PassThrough, Writable } from 'node:stream';
import { test } from 'node:test';

assert.ok(process.env.NODE_CANDIDATE_SITE, 'candidate site is required');
const site = resolve(process.env.NODE_CANDIDATE_SITE);
const require = createRequire(`${site}/package.json`);
const winston = require('winston');

function capture(options = {}) {
  const chunks = [];
  const stream = new Writable({
    write(chunk, encoding, callback) {
      chunks.push(Buffer.isBuffer(chunk) ? chunk.toString() : String(chunk));
      callback();
    },
  });
  const transport = new winston.transports.Stream({ stream });
  const logger = winston.createLogger({ transports: [transport], ...options });
  return {
    logger,
    chunks,
    finish() {
      return new Promise((resolve) => {
        logger.once('finish', resolve);
        logger.end();
      });
    },
  };
}

test('exports the package surface and version', () => {
  assert.equal(winston.version, '3.19.0');
  for (const key of ['createLogger', 'Logger', 'Container', 'Transport', 'format', 'transports', 'config', 'loggers']) {
    assert.ok(winston[key], key);
  }
  for (const key of ['Stream', 'Console', 'File', 'Http']) assert.equal(typeof winston.transports[key], 'function');
});

test('exposes the npm levels in severity order', () => {
  assert.deepEqual(winston.config.npm.levels, { error: 0, warn: 1, info: 2, http: 3, verbose: 4, debug: 5, silly: 6 });
  assert.equal(typeof winston.config.syslog.levels, 'object');
  assert.equal(typeof winston.config.cli.levels, 'object');
});

test('creates a logger with callable level methods', () => {
  const { logger } = capture();
  for (const key of ['error', 'warn', 'info', 'http', 'verbose', 'debug', 'silly', 'log']) assert.equal(typeof logger[key], 'function');
  assert.equal(logger.level, 'info');
  logger.close();
});

test('writes JSON records with metadata', async () => {
  const result = capture({ format: winston.format.json() });
  result.logger.info('hello', { requestId: 'r1', count: 2 });
  await result.finish();
  assert.deepEqual(JSON.parse(result.chunks[0]), { level: 'info', message: 'hello', requestId: 'r1', count: 2 });
});

test('writes simple formatted records', async () => {
  const result = capture({ format: winston.format.simple() });
  result.logger.warn('careful');
  await result.finish();
  assert.equal(result.chunks[0], 'warn: careful\n');
});

test('supports printf and combine in declaration order', async () => {
  const result = capture({
    format: winston.format.combine(
      winston.format.label({ label: 'api' }),
      winston.format.printf((info) => `${info.label}|${info.level}|${info.message}`),
    ),
  });
  result.logger.info('ready');
  await result.finish();
  assert.equal(result.chunks[0], 'api|info|ready\n');
});

test('merges default metadata and lets call metadata override it', async () => {
  const result = capture({ format: winston.format.json(), defaultMeta: { service: 'api', region: 'east' } });
  result.logger.info('hello', { region: 'west' });
  await result.finish();
  assert.deepEqual(JSON.parse(result.chunks[0]), { level: 'info', message: 'hello', service: 'api', region: 'west' });
});

test('filters levels at the configured threshold', async () => {
  const result = capture({ format: winston.format.json(), level: 'warn' });
  result.logger.info('hidden');
  result.logger.warn('shown');
  result.logger.error('also shown');
  await result.finish();
  assert.equal(result.chunks.length, 2);
  assert.deepEqual(result.chunks.map((chunk) => JSON.parse(chunk).level), ['warn', 'error']);
  assert.equal(result.logger.isLevelEnabled('info'), false);
  assert.equal(result.logger.isWarnEnabled(), true);
});

test('supports generic log overloads', async () => {
  const result = capture({ format: winston.format.json() });
  result.logger.log('info', 'first', { a: 1 });
  result.logger.log({ level: 'error', message: 'second', code: 'E2' });
  await result.finish();
  assert.deepEqual(result.chunks.map((chunk) => JSON.parse(chunk).message), ['first', 'second']);
});

test('supports child metadata inheritance', async () => {
  const result = capture({ format: winston.format.json(), defaultMeta: { service: 'root' } });
  const child = result.logger.child({ component: 'worker' });
  child.info('job', { jobId: 7 });
  await result.finish();
  assert.deepEqual(JSON.parse(result.chunks[0]), { level: 'info', message: 'job', service: 'root', component: 'worker', jobId: 7 });
});

test('supports errors format with error metadata', async () => {
  const result = capture({ format: winston.format.combine(winston.format.errors({ stack: true }), winston.format.json()) });
  const error = new Error('broken');
  result.logger.error(error);
  await result.finish();
  const record = JSON.parse(result.chunks[0]);
  assert.equal(record.message, 'broken');
  assert.match(record.stack, /Error: broken/);
});

test('supports splat interpolation', async () => {
  const result = capture({ format: winston.format.combine(winston.format.splat(), winston.format.simple()) });
  result.logger.info('hello %s %d', 'world', 3);
  await result.finish();
  assert.equal(result.chunks[0], 'info: hello world 3\n');
});

test('adds timestamps through a composable format', async () => {
  const result = capture({ format: winston.format.combine(winston.format.timestamp(), winston.format.json()) });
  result.logger.info('timed');
  await result.finish();
  const record = JSON.parse(result.chunks[0]);
  assert.equal(record.message, 'timed');
  assert.equal(typeof record.timestamp, 'string');
  assert.ok(Number.isNaN(Date.parse(record.timestamp)) === false);
});

test('supports a custom format transform', async () => {
  const addField = winston.format((info) => { info.marker = 'yes'; return info; });
  const result = capture({ format: winston.format.combine(addField(), winston.format.json()) });
  result.logger.info('marked');
  await result.finish();
  assert.equal(JSON.parse(result.chunks[0]).marker, 'yes');
});

test('supports silent loggers', async () => {
  const result = capture({ format: winston.format.json(), silent: true });
  result.logger.error('not emitted');
  await result.finish();
  assert.deepEqual(result.chunks, []);
});

test('adds and removes transports', async () => {
  const first = capture({ format: winston.format.json() });
  const secondStream = new PassThrough();
  const second = new winston.transports.Stream({ stream: secondStream });
  first.logger.add(second);
  first.logger.info('both');
  first.logger.remove(second);
  first.logger.info('first only');
  assert.equal(first.logger.transports.length, 1);
  await first.finish();
  assert.equal(first.chunks.length, 2);
});

test('clears transports', () => {
  const result = capture();
  assert.equal(result.logger.transports.length, 1);
  assert.equal(result.logger.clear(), result.logger);
  assert.equal(result.logger.transports.length, 0);
});

test('supports a custom transport callback', async () => {
  const records = [];
  class MemoryTransport extends winston.Transport {
    log(info, callback) { records.push({ level: info.level, message: info.message }); callback(); }
  }
  const logger = winston.createLogger({ transports: [new MemoryTransport()] });
  logger.info('memory');
  await new Promise((resolve) => { logger.once('finish', resolve); logger.end(); });
  assert.deepEqual(records, [{ level: 'info', message: 'memory' }]);
});

test('supports container get, has, and close', () => {
  const container = new winston.Container({ silent: true });
  const logger = container.get('worker');
  assert.equal(container.has('worker'), true);
  assert.equal(container.get('worker'), logger);
  container.close('worker');
  assert.equal(container.has('worker'), false);
});

test('supports the global loggers container without sharing new ids', () => {
  const id = `test-${process.pid}`;
  const logger = winston.loggers.add(id, { silent: true });
  assert.equal(winston.loggers.has(id), true);
  assert.equal(winston.loggers.get(id), logger);
  winston.loggers.close(id);
  assert.equal(winston.loggers.has(id), false);
});

test('supports startTimer completion shape', async () => {
  const result = capture({ format: winston.format.json() });
  const timer = result.logger.startTimer();
  assert.equal(typeof timer.done, 'function');
  timer.done({ operation: 'unit' });
  await result.finish();
  const record = JSON.parse(result.chunks[0]);
  assert.equal(record.operation, 'unit');
  assert.equal(record.level, 'info');
});

test('supports profile start and completion', async () => {
  const result = capture({ format: winston.format.json() });
  result.logger.profile('compile', { phase: 'start' });
  result.logger.profile('compile', { phase: 'done' });
  await result.finish();
  assert.equal(result.chunks.length, 1);
  assert.equal(JSON.parse(result.chunks[0]).phase, 'done');
});

test('supports configure to replace level and format', async () => {
  const result = capture({ format: winston.format.json(), level: 'error' });
  result.logger.configure({ format: winston.format.simple(), level: 'info', transports: result.logger.transports });
  result.logger.info('configured');
  await result.finish();
  assert.equal(result.chunks[0], 'info: configured\n');
});

test('preserves stream lifecycle and close', async () => {
  const result = capture({ format: winston.format.json() });
  let closed = false;
  result.logger.on('close', () => { closed = true; });
  result.logger.info('closing');
  await result.finish();
  result.logger.close();
  assert.equal(closed, true);
});
