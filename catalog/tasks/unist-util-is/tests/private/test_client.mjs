import {chmodSync, readFileSync, writeFileSync} from 'node:fs'
import {spawnSync} from 'node:child_process'

const ADAPTER_SOURCE = '/tests/private/candidate_adapter.txt'
const ADAPTER = '/tmp/unist-util-is-candidate-adapter.mjs'
const PACKAGE = 'unist-util-is'
let sequence = 0
let ready = false

function ensureAdapter() {
  if (ready) return
  const source = readFileSync(ADAPTER_SOURCE)
  try {
    writeFileSync(ADAPTER, source, {flag: 'wx', mode: 0o555})
  } catch (error) {
    if (error?.code !== 'EEXIST') throw error
  }
  chmodSync(ADAPTER, 0o555)
  ready = true
}

export function request(operation, payload = {}) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  ensureAdapter()

  const id = `request-${++sequence}`
  const input = JSON.stringify({id, operation, payload})
  if (Buffer.byteLength(input) > 64 * 1024) throw new Error('request exceeds bound')

  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM',
    '--kill-after=3s',
    '8s',
    'runuser',
    '-u',
    'candidate',
    '--',
    '/usr/bin/prlimit',
    '--cpu=8',
    '--nproc=32',
    '--nofile=128',
    '--',
    'env',
    '-i',
    'PATH=/usr/local/bin:/usr/bin:/bin',
    `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`,
    'CI=true',
    'LC_ALL=C.UTF-8',
    `NODE_ALLOWED_PACKAGE=${PACKAGE}`,
    '/usr/local/bin/node',
    '--no-addons',
    ADAPTER
  ], {
    cwd: site,
    input,
    encoding: 'utf8',
    maxBuffer: 512 * 1024,
    timeout: 12_000
  })

  if (result.error || !result.stdout) throw new Error('candidate child failed')
  let response
  try {
    response = JSON.parse(result.stdout)
  } catch {
    throw new Error('candidate response is malformed')
  }
  if (response?.id !== id) throw new Error('candidate response id mismatch')
  if (response.sentinel !== true) throw new Error('candidate sentinel behavior failed')
  return response
}
