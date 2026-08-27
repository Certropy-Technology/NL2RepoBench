import { readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.argv[2] ?? '/workspace';
const packagePath = join(root, 'package.json');
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));

for (const key of [
  'devDependencies',
  'peerDependencies',
  'peerDependenciesMeta',
  'allowScripts',
]) {
  delete packageJson[key];
}

// Test and lint commands are harmless, but no lifecycle hook is needed by the
// published runtime. Keep the Oracle distribution identical to the contract.
delete packageJson.scripts;
writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`, { mode: 0o644 });
rmSync(join(root, '.npmrc'), { force: true });

const lock = {
  name: 'ws',
  version: '8.21.3',
  lockfileVersion: 3,
  requires: true,
  packages: {
    '': {
      name: 'ws',
      version: '8.21.3',
    },
  },
};
writeFileSync(join(root, 'package-lock.json'), `${JSON.stringify(lock, null, 2)}\n`, {
  mode: 0o644,
});

for (const relative of ['.git', '.github', 'benchmark', 'test']) {
  rmSync(join(root, relative), { recursive: true, force: true });
}
