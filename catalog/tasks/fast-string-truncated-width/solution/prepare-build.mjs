import {readFileSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';

const [workspace, buildLockPath] = process.argv.slice(2);
if (!workspace || !buildLockPath) throw new Error('workspace and build lock are required');

const packagePath = join(workspace, 'package.json');
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));
if (
	packageJson.name !== 'fast-string-truncated-width'
	|| packageJson.version !== '3.0.3'
	|| packageJson.license !== 'MIT'
) {
	throw new Error('frozen package metadata does not match the task contract');
}

packageJson.scripts = {build: 'tsc -p tsconfig.build.json'};
packageJson.devDependencies = {typescript: '5.9.3'};
delete packageJson.dependencies;
delete packageJson.workspaces;
packageJson.files = ['dist', 'license', 'readme.md'];
writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`);

const indexPath = join(workspace, 'src', 'index.ts');
let indexSource = readFileSync(indexPath, 'utf8');
const original = indexSource;
indexSource = indexSource
	.replace("from './utils';", "from './utils.js';")
	.replace("from './types';", "from './types.js';");
if (indexSource === original || !indexSource.includes("from './utils.js';") || !indexSource.includes("from './types.js';")) {
	throw new Error('frozen TypeScript import adaptation did not apply');
}
writeFileSync(indexPath, indexSource);

const tsconfig = {
	compilerOptions: {
		target: 'ES2022',
		module: 'NodeNext',
		moduleResolution: 'NodeNext',
		strict: true,
		declaration: true,
		declarationMap: false,
		sourceMap: false,
		outDir: 'dist',
		rootDir: 'src',
		skipLibCheck: true,
		verbatimModuleSyntax: true,
	},
	include: ['src/**/*.ts'],
};
writeFileSync(join(workspace, 'tsconfig.build.json'), `${JSON.stringify(tsconfig, null, 2)}\n`);

const lock = JSON.parse(readFileSync(buildLockPath, 'utf8'));
lock.name = packageJson.name;
lock.version = packageJson.version;
lock.packages[''] = {
	name: packageJson.name,
	version: packageJson.version,
	license: 'MIT',
	devDependencies: {typescript: '5.9.3'},
};
writeFileSync(join(workspace, 'package-lock.json'), `${JSON.stringify(lock, null, 2)}\n`);
