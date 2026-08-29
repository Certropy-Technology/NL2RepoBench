import {chmodSync, readFileSync, writeFileSync} from 'node:fs'
import {spawnSync} from 'node:child_process'

const ADAPTER_SOURCE = '/tests/private/candidate_adapter.txt'
const ADAPTER = '/tmp/mdast-util-to-hast-candidate-adapter.mjs'
const PACKAGE = 'mdast-util-to-hast'
let sequence = 0
let ready = false

function ensureAdapter() {
  if (ready) return
  const source = readFileSync(ADAPTER_SOURCE)
  try { writeFileSync(ADAPTER, source, {flag: 'wx', mode: 0o555}) } catch (error) {
    if (error?.code !== 'EEXIST') throw error
  }
  chmodSync(ADAPTER, 0o555)
  ready = true
}

function request(operation, payload) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  ensureAdapter()
  const id = `request-${++sequence}`
  const input = JSON.stringify({id, operation, payload})
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, 'CI=true', 'LC_ALL=C.UTF-8',
    `NODE_ALLOWED_PACKAGE=${PACKAGE}`, '/usr/local/bin/node', '--no-addons', ADAPTER
  ], {cwd: site, input, encoding: 'utf8', maxBuffer: 512 * 1024, timeout: 35_000})
  if (result.error || !result.stdout) throw new Error('candidate child failed')
  const response = JSON.parse(result.stdout)
  if (response?.id !== id) throw new Error('candidate response id mismatch')
  return response
}

export function call(exportName, args) { return request('call', {export: exportName, args}) }
export function inventory() { return request('inventory', {}) }
