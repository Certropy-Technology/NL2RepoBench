import { createRequire } from 'node:module';
import { mkdtempSync, mkdirSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

export function loadRollup() {
  const root = process.env.NODE_CANDIDATE_SITE;
  if (!root) throw new Error('NODE_CANDIDATE_SITE is missing');
  return createRequire(join(root, 'package.json'))('rollup');
}

export function project(files) {
  const root = mkdtempSync(join(tmpdir(), 'rollup-test-'));
  for (const [name, contents] of Object.entries(files)) {
    const path = join(root, name);
    const parent = path.slice(0, path.lastIndexOf('/'));
    if (parent !== root) mkdirSync(parent, { recursive: true });
    writeFileSync(path, contents);
  }
  return root;
}
