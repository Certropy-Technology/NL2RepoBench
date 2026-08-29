import {readFileSync, writeFileSync} from 'node:fs';
const path = process.argv[2];
const packageJson = JSON.parse(readFileSync(path, 'utf8'));
for (const key of ['scripts', 'devDependencies', 'bin', 'engines']) delete packageJson[key];
writeFileSync(path, JSON.stringify(packageJson, null, 2) + '\n');
