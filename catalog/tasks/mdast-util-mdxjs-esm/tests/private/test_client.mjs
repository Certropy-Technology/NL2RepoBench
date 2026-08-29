import {spawnSync} from 'node:child_process'

const node = '/usr/local/bin/node'
const runnerCode = `import {readFileSync} from 'node:fs'
import {join} from 'node:path'
import {pathToFileURL} from 'node:url'
const site = process.env.NODE_CANDIDATE_SITE
const request = JSON.parse(readFileSync(0, 'utf8'))
const modulePath = pathToFileURL(join(site, 'node_modules/mdast-util-mdxjs-esm/adapter.js')).href
const adapter = await import(modulePath)
try {
  const value = await adapter.run(request)
  process.stdout.write(JSON.stringify({ok: true, value}) + '\\n')
} catch (error) {
  process.stdout.write(JSON.stringify({ok: false, name: error?.constructor?.name ?? 'Error', message: String(error?.message ?? error)}) + '\\n')
  process.exitCode = 1
}`

export function callAdapter(request) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const result = spawnSync('/usr/bin/timeout', ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--', '/usr/bin/prlimit', '--cpu=60', '--nproc=32', '--nofile=128', '--', 'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`, `NODE_CANDIDATE_SITE=${site}`, node, '--no-addons', '--input-type=module', '-e', runnerCode], {cwd: site, input: JSON.stringify(request), encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000})
  if (result.error) throw result.error
  const line = (result.stdout ?? '').trim().split(/\r?\n/).at(-1)
  if (!line) throw new Error('adapter produced no response')
  const payload = JSON.parse(line)
  if (!payload.ok) throw new Error(payload.message ?? 'candidate-call-failed')
  return payload.value
}

export function callAdapterExpectError(request) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const result = spawnSync('/usr/bin/timeout', ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--', '/usr/bin/prlimit', '--cpu=60', '--nproc=32', '--nofile=128', '--', 'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`, `NODE_CANDIDATE_SITE=${site}`, node, '--no-addons', '--input-type=module', '-e', runnerCode], {cwd: site, input: JSON.stringify(request), encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000})
  const line = (result.stdout ?? '').trim().split(/\r?\n/).at(-1)
  if (!line) throw new Error('adapter produced no response')
  const payload = JSON.parse(line)
  if (payload.ok) throw new Error('expected adapter failure')
  return payload
}
