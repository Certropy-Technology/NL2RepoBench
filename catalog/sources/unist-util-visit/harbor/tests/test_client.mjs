import {spawnSync} from 'node:child_process'

const NODE = '/usr/local/bin/node'
const TIMEOUT = '/usr/bin/timeout'

export function walk(request) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const adapter = `${site}/node_modules/unist-util-visit/adapter.mjs`
  const result = spawnSync(TIMEOUT, [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, NODE, '--no-addons', adapter
  ], {
    cwd: site,
    input: `${JSON.stringify(request)}\n`,
    encoding: 'utf8',
    maxBuffer: 256 * 1024,
    timeout: 35_000
  })
  if (result.error) throw result.error
  if (result.status !== 0) {
    throw new Error(`candidate adapter failed: ${result.stderr || result.status}`)
  }
  try {
    return JSON.parse(result.stdout)
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`)
  }
}
