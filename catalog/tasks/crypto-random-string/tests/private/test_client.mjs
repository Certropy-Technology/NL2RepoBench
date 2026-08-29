import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';

export function call(request) {
  if (request.op === 'metadata') {
    const packageJson = JSON.parse(readFileSync(join(process.env.NODE_CANDIDATE_SITE, 'node_modules', 'crypto-random-string', 'package.json'), 'utf8'));
    return {ok: true, value: packageJson};
  }
  const site = process.env.NODE_CANDIDATE_SITE;
  const isContract = request.op === 'contract';
  const runner = isContract
    ? readFileSync(new URL('./contract_runner', import.meta.url), 'utf8')
    : '/tests/runtime/node/candidate_runner.mjs';
  const input = isContract
    ? request
    : {package: 'crypto-random-string', export: 'default', args: request.args};
  const command = isContract
    ? 'cd "$1" && exec "$2" --input-type=module --eval "$3"'
    : 'cd "$1" && exec "$2" "$3"';
  const result = spawnSync('/usr/sbin/runuser', ['-u', 'candidate', '--', '/bin/sh', '-c', command, 'candidate-runner', site, process.execPath, runner], {
    cwd: site,
    input: JSON.stringify(input),
    encoding: 'utf8',
    timeout: 30_000,
    maxBuffer: 300_000,
    env: {...process.env, NODE_OPTIONS: undefined, NODE_PATH: undefined},
  });
  const line = (result.stdout ?? '').trim().split(/\r?\n/).at(-1);
  if (!line) throw new Error(`adapter did not respond: ${result.stderr ?? result.error ?? 'unknown error'}`);
  return JSON.parse(line);
}
