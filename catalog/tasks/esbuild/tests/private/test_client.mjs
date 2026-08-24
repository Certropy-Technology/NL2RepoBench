import { spawnSync } from 'node:child_process';

const candidate = process.env.NODE_CANDIDATE_SITE;
const runner = process.env.NODE_CANDIDATE_RUNNER || '/tests/runtime/node/candidate_runner.mjs';

export function call(exportName, args = []) {
  const result = spawnSync(
    process.execPath,
    ['--no-addons', runner],
    {
      cwd: candidate,
      env: {
        PATH: '/usr/local/bin:/usr/bin:/bin',
        HOME: `${candidate}/.home`,
        TMPDIR: `${candidate}/.tmp`,
        NODE_ALLOWED_PACKAGE: 'esbuild',
      },
      input: JSON.stringify({ package: 'esbuild', export: exportName, args }) + '\n',
      encoding: 'utf8',
      timeout: 30_000,
      maxBuffer: 256 * 1024,
    },
  );
  if (result.error) throw result.error;
  const lines = (result.stdout || '').trim().split(/\r?\n/);
  const payload = JSON.parse(lines.at(-1) || '{}');
  if (!payload.ok) {
    const error = new Error(payload.message || payload.error || 'candidate call failed');
    error.name = payload.exception_type || 'CandidateError';
    throw error;
  }
  return payload.value;
}

export function callError(exportName, args = []) {
  const result = spawnSync(
    process.execPath,
    ['--no-addons', runner],
    {
      cwd: candidate,
      env: {
        PATH: '/usr/local/bin:/usr/bin:/bin',
        HOME: `${candidate}/.home`,
        TMPDIR: `${candidate}/.tmp`,
        NODE_ALLOWED_PACKAGE: 'esbuild',
      },
      input: JSON.stringify({ package: 'esbuild', export: exportName, args }) + '\n',
      encoding: 'utf8',
      timeout: 30_000,
      maxBuffer: 256 * 1024,
    },
  );
  const lines = (result.stdout || '').trim().split(/\r?\n/);
  return JSON.parse(lines.at(-1) || '{}');
}
