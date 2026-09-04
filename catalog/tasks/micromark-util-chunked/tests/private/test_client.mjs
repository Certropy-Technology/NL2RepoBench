import {spawnSync} from 'node:child_process'

const NODE = '/usr/local/bin/node'
const ADAPTER = String.raw`
import {createRequire} from 'node:module'
import {pathToFileURL} from 'node:url'
import {readFileSync} from 'node:fs'
import {join} from 'node:path'
const input = JSON.parse(readFileSync(0, 'utf8'))
const require = createRequire(pathToFileURL(process.cwd() + '/package.json'))
let candidate
try { candidate = require('micromark-util-chunked') }
catch (error) {
  if (error?.code !== 'ERR_REQUIRE_ESM' && error?.code !== 'ERR_PACKAGE_PATH_NOT_EXPORTED') throw error
  const root = join(process.cwd(), 'node_modules', 'micromark-util-chunked')
  const manifest = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'))
  const entry = typeof manifest.exports === 'string' ? manifest.exports : manifest.exports?.['.']?.import ?? manifest.exports?.import ?? manifest.module ?? manifest.main
  if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) throw new Error('unsafe-entry')
  candidate = await import(pathToFileURL(join(root, entry)).href)
}
const list = input.list
const items = input.items
let result
if (input.operation === 'splice') result = await candidate.splice(list, input.start, input.remove, items)
else if (input.operation === 'push') result = await candidate.push(list, items)
else throw new Error('unsupported-operation')
process.stdout.write(JSON.stringify({list, result, sameAsList: result === list, sameAsItems: result === items}) + '\n')
`

export function invoke(payload) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=60', '--nproc=32', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`,
    NODE, '--no-addons', '--input-type=module', '--eval', ADAPTER
  ], {cwd: site, input: JSON.stringify(payload) + '\n', encoding: 'utf8', maxBuffer: 2 * 1024 * 1024, timeout: 30_000})
  if (result.error) throw result.error
  if (result.status !== 0) throw new Error(`candidate-call-failed: ${result.stderr}`)
  return JSON.parse(result.stdout)
}
