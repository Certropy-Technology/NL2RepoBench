import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {Readable} from 'node:stream';

function emit(payload, code = 0) {
  process.stdout.write(`${JSON.stringify(payload)}\n`);
  process.exit(code);
}

function encode(value) {
  if (Buffer.isBuffer(value)) return {type: 'Buffer', data: [...value]};
  if (value instanceof ArrayBuffer) return {type: 'ArrayBuffer', data: [...new Uint8Array(value)]};
  if (ArrayBuffer.isView(value)) return {type: value.constructor.name, data: [...new Uint8Array(value.buffer, value.byteOffset, value.byteLength)]};
  if (Array.isArray(value)) return value.map(encode);
  return value;
}

async function loadCandidate() {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('NODE_CANDIDATE_SITE is missing');
  const root = join(site, 'node_modules', 'get-stream');
  const manifest = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  const rootExport = manifest.exports?.['.'] ?? manifest.exports;
  const entry = typeof rootExport === 'string'
    ? rootExport
    : rootExport?.default ?? rootExport?.import ?? manifest.module ?? manifest.main;
  if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) {
    throw new Error('package has no safe root export');
  }
  return import(pathToFileURL(join(root, entry)).href);
}

const request = JSON.parse(process.env.GET_STREAM_REQUEST_JSON ?? 'null');
if (request !== null && (typeof request !== 'object' || typeof request.operation !== 'string')) {
  emit({ok: false, fatal: 'request is invalid'}, 1);
}

function nodeStream(chunks, options = {}) {
  return Readable.from(chunks, options);
}

function webStream(chunks) {
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(chunk);
      controller.close();
    },
  });
}

function errorStream(chunk, message) {
  return new Readable({
    read() {
      this.push(chunk);
      this.destroy(new Error(message));
    },
  });
}

async function invoke(candidate) {
  const {operation} = request;
  const asText = candidate.default;
  const asBuffer = candidate.getStreamAsBuffer;
  const asArrayBuffer = candidate.getStreamAsArrayBuffer;
  const asArray = candidate.getStreamAsArray;
  const ops = {
    textBasic: () => asText(nodeStream(['hello', ' world'])),
    textUtf8Split: () => asText(nodeStream([Buffer.from([0xF0, 0x9F]), Buffer.from([0x8C, 0x8D])])),
    textArrayBuffer: () => asText(nodeStream([new Uint8Array([0x68, 0x69]).buffer])),
    textTypedOffset: () => asText(nodeStream([new Uint8Array(Buffer.from('xhello')).subarray(1, 6)])),
    textWeb: () => asText(webStream(['web', ' stream'])),
    textAsync: async () => asText((async function* () { yield 'async'; yield ' iterable'; })()),
    textMax: async () => { try { await asText(nodeStream(['abcd']), {maxBuffer: 3}); return {unexpected: true}; } catch (error) { return {name: error.name, message: error.message, bufferedData: encode(error.bufferedData)}; } },
    bufferBasic: () => asBuffer(nodeStream(['hello', Buffer.from(' world')])),
    bufferTypedOffset: () => asBuffer(nodeStream([new Uint8Array([88, 97, 98, 99, 89]).subarray(1, 4)])),
    bufferArrayBuffer: () => asBuffer(nodeStream([Uint8Array.from([1, 2, 3]).buffer])),
    bufferMax: async () => { try { await asBuffer(nodeStream([Buffer.from([1, 2, 3, 4])]), {maxBuffer: 3}); return {unexpected: true}; } catch (error) { return {name: error.name, bufferedData: encode(error.bufferedData)}; } },
    bufferError: async () => { try { await asBuffer(errorStream(Buffer.from('partial'), 'boom')); return {unexpected: true}; } catch (error) { return {name: error.name, message: error.message, bufferedData: encode(error.bufferedData)}; } },
    arrayBufferBasic: async () => encode(await asArrayBuffer(nodeStream(['a', Buffer.from('bc')]))),
    arrayBufferTypedOffset: async () => encode(await asArrayBuffer(nodeStream([new Uint8Array([0, 10, 11, 12, 0]).subarray(1, 4)]))),
    arrayBufferMax: async () => { try { await asArrayBuffer(nodeStream([Buffer.from([1, 2, 3])]), {maxBuffer: 2}); return {unexpected: true}; } catch (error) { return {name: error.name, bufferedData: encode(error.bufferedData)}; } },
    arrayValues: () => asArray(nodeStream(['a', 'b', 'c'])),
    arrayObjects: () => asArray(nodeStream([{id: 1}, {id: 2}], {objectMode: true})),
    arrayMixed: () => asArray(nodeStream(['a', Buffer.from('b'), {id: 3}], {objectMode: true})),
    arrayMax: async () => { try { await asArray(nodeStream([1, 2, 3], {objectMode: true}), {maxBuffer: 2}); return {unexpected: true}; } catch (error) { return {name: error.name, bufferedData: encode(error.bufferedData)}; } },
    webEnded: () => asText(new ReadableStream({start(controller) { controller.close(); }})),
    webArrayBuffer: async () => encode(await asArrayBuffer(webStream([new Uint8Array([4, 5])]))),
    webArray: () => asArray(webStream(['x', 'y'])),
    asyncObjects: () => asArray((async function* () { yield {kind: 'a'}; yield {kind: 'b'}; })()),
    nodeEnded: () => { const stream = nodeStream([]); stream.resume(); return asText(stream); },
    concurrent: async () => { const stream = nodeStream(['same']); const results = await Promise.all([asText(stream), asText(stream)]); return results; },
    textError: async () => { try { await asText(errorStream(Buffer.from('partial'), 'boom')); return {unexpected: true}; } catch (error) { return {name: error.name, message: error.message, bufferedData: encode(error.bufferedData)}; } },
    asyncCleanup: async () => { let returned = false; const iterable = {async next() { return {done: false, value: 'x'}; }, async return() { returned = true; return {done: true}; }, [Symbol.asyncIterator]() { return this; }}; try { await asText(iterable, {maxBuffer: 0}); } catch {} return returned; },
    invalidInput: async () => { try { await asText('not a stream'); return {unexpected: true}; } catch (error) { return {name: error.name, message: error.message}; } },
    objectText: async () => { try { await asText(nodeStream([{id: 1}], {objectMode: true})); return {unexpected: true}; } catch (error) { return {name: error.name, message: error.message}; } },
    exports: () => ({default: typeof asText, buffer: typeof asBuffer, arrayBuffer: typeof asArrayBuffer, array: typeof asArray, maxBufferError: candidate.MaxBufferError?.name}),
  };
  if (!ops[operation]) throw new Error(`unknown operation: ${operation}`);
  return encode(await ops[operation]());
}

export function callCandidate(operation) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const source = readFileSync(fileURLToPath(import.meta.url), 'utf8');
  const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
  const result = spawnSync(
    '/usr/bin/timeout',
    ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
      '/usr/bin/prlimit', '--cpu=60', '--nproc=4096', '--nofile=128', '--',
      'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `NODE_CANDIDATE_SITE=${site}`, `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`, `GET_STREAM_REQUEST_JSON=${JSON.stringify({operation})}`,
      process.execPath, '--no-addons', '--input-type=module', '--eval', `import(${JSON.stringify(moduleUrl)})`,
    ],
    {cwd: site, encoding: 'utf8', maxBuffer: 256 * 1024},
  );
  if (result.error) throw result.error;
  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stderr ?? result.stdout}`);
  }
  if (result.status !== 0 || payload.ok !== true) {
    throw new Error(payload.fatal ?? 'candidate call failed');
  }
  return payload.value;
}

if (request !== null) {
  try {
    const candidate = await loadCandidate();
    emit({ok: true, value: await invoke(candidate)});
  } catch (error) {
    emit({ok: false, fatal: `${error?.name ?? 'Error'}: ${error?.message ?? error}`}, 1);
  }
}
