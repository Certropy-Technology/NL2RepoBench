import {readFileSync, writeFileSync} from 'node:fs'

const path = '/workspace/package.json'
const packageJson = JSON.parse(readFileSync(path, 'utf8'))
packageJson.name = 'mdast-util-find-and-replace'
packageJson.version = '3.0.2'
packageJson.type = 'module'
packageJson.exports = {types: './index.d.ts', default: './index.js'}
packageJson.files = [
  'index.js',
  'index.d.ts',
  'index.d.ts.map',
  'lib/index.js',
  'lib/index.d.ts',
  'lib/index.d.ts.map'
]
packageJson.sideEffects = false
packageJson.dependencies = {
  '@types/mdast': '4.0.4',
  'escape-string-regexp': '5.0.0',
  'unist-util-is': '6.0.1',
  'unist-util-visit-parents': '6.0.2'
}
delete packageJson.devDependencies
delete packageJson.scripts
delete packageJson.workspaces
delete packageJson.prettier
delete packageJson.remarkConfig
delete packageJson.typeCoverage
delete packageJson.xo
writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`)
