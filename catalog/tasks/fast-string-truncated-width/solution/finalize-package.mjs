import {readFileSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';

const [workspace] = process.argv.slice(2);
if (!workspace) throw new Error('workspace is required');

const packagePath = join(workspace, 'package.json');
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));
delete packageJson.scripts;
delete packageJson.devDependencies;
delete packageJson.dependencies;
writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`);

const lock = {
	name: packageJson.name,
	version: packageJson.version,
	lockfileVersion: 3,
	requires: true,
	packages: {
		'': {
			name: packageJson.name,
			version: packageJson.version,
			license: 'MIT',
		},
	},
};
writeFileSync(join(workspace, 'package-lock.json'), `${JSON.stringify(lock, null, 2)}\n`);
