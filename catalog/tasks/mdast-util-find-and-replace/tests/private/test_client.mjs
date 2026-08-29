import {spawnSync} from 'node:child_process'
import {chmodSync, copyFileSync} from 'node:fs'

const NODE = '/usr/local/bin/node'
const ADAPTER = '/tmp/nl2repobench-mdast-find-replace-adapter.mjs'
const ADAPTER_SOURCE = new URL('./adapter-source.js.txt', import.meta.url)
const TOTAL_BUDGET_MS = 45_000
const startedAt = Date.now()

copyFileSync(ADAPTER_SOURCE, ADAPTER)
chmodSync(ADAPTER, 0o555)

export function scenario(operation, payload = {}) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const encoded = JSON.stringify({operation, ...payload})
  if (Buffer.byteLength(encoded) > 64 * 1024) {
    throw new Error('request exceeds the bound')
  }

  const remaining = TOTAL_BUDGET_MS - (Date.now() - startedAt)
  if (remaining < 500) throw new Error('candidate cumulative call budget exhausted')
  const callSeconds = Math.max(1, Math.min(6, Math.ceil(remaining / 1000)))
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM',
    '--kill-after=2s',
    `${callSeconds}s`,
    'runuser',
    '-u',
    'candidate',
    '--',
    '/usr/bin/prlimit',
    '--cpu=6',
    '--nproc=32',
    '--nofile=128',
    '--as=2147483648',
    '--',
    '/usr/bin/env',
    '-i',
    'PATH=/usr/local/bin:/usr/bin:/bin',
    `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`,
    'LC_ALL=C.UTF-8',
    NODE,
    '--no-addons',
    ADAPTER
  ], {
    cwd: site,
    input: `${encoded}\n`,
    encoding: 'utf8',
    maxBuffer: 512 * 1024,
    timeout: (callSeconds + 3) * 1000
  })

  if (result.error || !result.stdout) throw new Error('candidate child failed')
  let response
  try {
    response = JSON.parse(result.stdout)
  } catch {
    throw new Error('candidate child returned malformed JSON')
  }
  if (!response?.ok) throw new Error(response?.message ?? 'candidate call failed')
  return response.value
}
