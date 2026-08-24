import assert from 'node:assert/strict';
import { test } from 'node:test';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

test('CLI bundles a local input to a file', () => {
  const site = process.env.NODE_CANDIDATE_SITE;
  const root = mkdtempSync(join(tmpdir(), 'rollup-cli-'));
  const input = join(root, 'main.js');
  const output = join(root, 'bundle.js');
  writeFileSync(input, 'export const cliValue = 3;\n');
  const bin = join(site, 'node_modules', 'rollup', 'dist', 'bin', 'rollup');
  execFileSync(process.execPath, [bin, input, '--format', 'cjs', '--file', output], { cwd: root });
  assert.match(readFileSync(output, 'utf8'), /cliValue/);
});
