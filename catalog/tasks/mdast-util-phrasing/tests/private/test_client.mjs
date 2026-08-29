import {chmodSync, copyFileSync, mkdirSync} from 'node:fs'
import {spawnSync} from 'node:child_process'

const privateRoot = '/tests/private'
const adapterRoot = '/tmp/mdast-util-phrasing-adapter'
const adapterPath = `${adapterRoot}/candidate_adapter.mjs`
const site = process.env.NODE_CANDIDATE_SITE
let cumulativeMilliseconds = 0

mkdirSync(adapterRoot, {recursive: true, mode: 0o755})
copyFileSync(`${privateRoot}/candidate_adapter.mjs.txt`, adapterPath)
chmodSync(adapterPath, 0o555)

function request(payload) {
  if (!site) throw new Error('candidate site is not configured')
  if (cumulativeMilliseconds >= 5000) throw new Error('candidate call budget exhausted')
  const started = Date.now()
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=1s', '1s',
    'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=3', '--nproc=32', '--nofile=128', '--fsize=1048576', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`,
    'LC_ALL=C.UTF-8', `NODE_CANDIDATE_SITE=${site}`, 'NODE_ALLOWED_PACKAGE=mdast-util-phrasing',
    '/usr/local/bin/node', '--no-addons', adapterPath
  ], {
    cwd: site,
    input: `${JSON.stringify(payload)}\n`,
    encoding: 'utf8',
    maxBuffer: 256 * 1024,
    timeout: 1500
  })
  cumulativeMilliseconds += Date.now() - started
  if (result.error || !result.stdout) throw new Error('candidate child failed')
  let response
  try {
    response = JSON.parse(result.stdout)
  } catch {
    throw new Error('candidate child returned malformed JSON')
  }
  if (!response.ok) throw new Error(response.message ?? response.error ?? 'candidate call failed')
  return response.value === undefined ? response : response
}

export function inventory() {
  return request({operation: 'inventory'}).value
}

export function classify(value, hasValue = true) {
  const payload = {operation: 'call'}
  if (hasValue) payload.value = value
  return request(payload)
}
