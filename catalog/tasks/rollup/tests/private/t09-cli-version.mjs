import assert from 'node:assert/strict';
import { test } from 'node:test';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { join } from 'node:path';

test('CLI reports the frozen version', () => {
  const root = process.env.NODE_CANDIDATE_SITE;
  const pkg = createRequire(join(root, 'package.json'))('rollup/package.json');
  const bin = join(root, 'node_modules', 'rollup', pkg.bin.rollup);
  const output = execFileSync(process.execPath, [bin, '--version'], { encoding: 'utf8' });
  assert.equal(output.trim(), 'rollup v4.62.5');
});
