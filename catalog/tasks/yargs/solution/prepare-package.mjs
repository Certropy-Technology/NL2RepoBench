import {readFileSync, writeFileSync} from 'node:fs';

const path = process.argv[2];
if (!path) throw new Error('package path is required');

const packageJson = JSON.parse(readFileSync(path, 'utf8'));
if (packageJson.name !== 'yargs' || packageJson.version !== '18.1.0' || packageJson.type !== 'module') {
  throw new Error('unexpected frozen package identity');
}

packageJson.dependencies = {
  cliui: '9.0.1',
  escalade: '3.2.0',
  'get-caller-file': '2.0.5',
  'string-width': '8.2.1',
  y18n: '5.0.8',
  'yargs-parser': '22.0.0',
};
delete packageJson.devDependencies;
delete packageJson.scripts;
delete packageJson.nyc;
writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`, {mode: 0o444});
