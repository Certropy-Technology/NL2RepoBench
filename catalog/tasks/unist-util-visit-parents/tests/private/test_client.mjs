import {spawnSync} from 'node:child_process'
import {chmodSync, readFileSync, writeFileSync} from 'node:fs'

const ADAPTER_SOURCE = '/tests/private/candidate_adapter.source'
const ADAPTER = '/tmp/nl2repobench-unist-util-visit-parents-adapter.mjs'
const MAX_BYTES = 512 * 1024
let fatalResponse
let adapterReady = false

function prepareAdapter() {
  if (adapterReady) return
  writeFileSync(ADAPTER, readFileSync(ADAPTER_SOURCE), {flag: 'wx', mode: 0o500})
  chmodSync(ADAPTER, 0o500)
  adapterReady = true
}

export function callCandidate(request) {
  if (fatalResponse) return fatalResponse
  prepareAdapter()
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const input = `${JSON.stringify(request)}\n`
  if (Buffer.byteLength(input) > 64 * 1024) throw new Error('test request exceeds bound')
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM',
    '--kill-after=2s',
    '6s',
    '/usr/bin/prlimit',
    '--cpu=6',
    '--nproc=32',
    '--nofile=128',
    '--',
    'env',
    '-i',
    'PATH=/usr/local/bin:/usr/bin:/bin',
    `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`,
    '/usr/local/bin/node',
    '--no-addons',
    ADAPTER
  ], {
    cwd: site,
    input,
    encoding: 'utf8',
    maxBuffer: MAX_BYTES,
    timeout: 9_000
  })
  if (result.error || result.signal || result.status === 124 || result.status === 137) {
    fatalResponse = {
      ok: false,
      error: 'candidate-call-failed',
      message: result.error?.message ?? `candidate process terminated (${result.status ?? result.signal})`
    }
    return fatalResponse
  }
  try {
    const response = JSON.parse(result.stdout)
    if (!response || typeof response.ok !== 'boolean') throw new Error('invalid response')
    return response
  } catch {
    fatalResponse = {
      ok: false,
      error: 'candidate-call-failed',
      message: `candidate response malformed: ${String(result.stdout).slice(0, 200)}`
    }
    return fatalResponse
  }
}
