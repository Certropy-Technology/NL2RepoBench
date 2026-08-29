import {spawnSync} from 'node:child_process';

const NODE = process.execPath;
const MAX_RESPONSE_BYTES = 256 * 1024;
const ADAPTER = String.raw`
import {createRequire} from 'node:module';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';

function emit(payload, code = 0) {
  process.stdout.write(JSON.stringify(payload) + '\n');
  process.exit(code);
}

async function loadCandidate() {
  const require = createRequire(pathToFileURL(join(process.cwd(), 'package.json')));
  try {
    return require('detect-indent');
  } catch (error) {
    if (error?.code !== 'ERR_REQUIRE_ESM' && error?.code !== 'ERR_PACKAGE_PATH_NOT_EXPORTED') throw error;
    const root = join(process.cwd(), 'node_modules', 'detect-indent');
    const manifest = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
    const exports = manifest.exports;
    const entry = typeof exports === 'string'
      ? exports
      : exports?.['.']?.import ?? exports?.import ?? manifest.module ?? manifest.main;
    if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) {
      throw new Error('package has no safe root export');
    }
    return import(pathToFileURL(join(root, entry)).href);
  }
}

try {
  const request = JSON.parse(process.env.DETECT_INDENT_REQUEST_JSON ?? 'null');
  if (!request || typeof request !== 'object' || !Object.hasOwn(request, 'value')) {
    throw new TypeError('request is invalid');
  }
  const candidate = await loadCandidate();
  const detectIndent = candidate.default ?? candidate;
  if (typeof detectIndent !== 'function') throw new TypeError('default export is not callable');
  const result = detectIndent(request.value);
  if (!result || typeof result !== 'object' || Array.isArray(result)) {
    throw new TypeError('result must be an object');
  }
  emit({ok: true, value: {
    amount: result.amount,
    type: result.type === undefined ? null : result.type,
    indent: result.indent,
  }});
} catch (error) {
  emit({ok: false, exceptionType: error?.constructor?.name ?? 'Error', message: String(error?.message ?? error).slice(0, 512)}, 1);
}
`;

export function callCandidate(value) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const request = JSON.stringify({value});
  const result = spawnSync(
    '/usr/bin/timeout',
    ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
      '/usr/bin/prlimit', '--cpu=60', '--nproc=4096', '--nofile=128', '--',
      'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`, `DETECT_INDENT_REQUEST_JSON=${request}`,
      NODE, '--no-addons', '--input-type=module', '--eval', ADAPTER],
    {cwd: site, encoding: 'utf8', maxBuffer: MAX_RESPONSE_BYTES},
  );
  if (result.error) throw result.error;
  if (Buffer.byteLength(result.stdout ?? '') > MAX_RESPONSE_BYTES) {
    throw new Error('candidate response exceeds the size limit');
  }
  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stderr ?? result.stdout}`);
  }
  if (result.status !== 0 || payload.ok !== true) {
    const error = new Error(payload.message ?? 'candidate call failed');
    error.name = payload.exceptionType ?? 'CandidateCallError';
    throw error;
  }
  return payload.value;
}
