import {chmodSync, readFileSync, writeFileSync} from 'node:fs'
import {spawnSync} from 'node:child_process'
import {join} from 'node:path'
let sequence = 0
let ready = false
function ensureAdapter() {
  if (ready) return
  const target = '/tmp/hast-util-to-estree-candidate-adapter.mjs'
  try { writeFileSync(target, readFileSync('/tests/private/candidate_adapter.txt'), {flag: 'wx', mode: 0o555}) } catch (error) { if (error?.code !== 'EEXIST') throw error }
  chmodSync(target, 0o555)
  ready = true
}
function request(operation, payload) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  ensureAdapter()
  const id = `request-${++sequence}`
  const result = spawnSync('/usr/bin/timeout', ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--', '/usr/bin/prlimit', '--cpu=30', '--nproc=64', '--nofile=128', '--', 'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`, 'CI=true', 'LC_ALL=C.UTF-8', '/usr/local/bin/node', '--no-addons', '/tmp/hast-util-to-estree-candidate-adapter.mjs'], {cwd: site, input: JSON.stringify({id, operation, payload}), encoding: 'utf8', maxBuffer: 1048576, timeout: 35000})
  if (result.error || !result.stdout) throw new Error('candidate child failed')
  const response = JSON.parse(result.stdout)
  if (response.id !== id) throw new Error('candidate response id mismatch')
  return response
}
export function call(exportName, args) { return request('call', {export: exportName, args}) }
export function inventory() { return request('inventory', {}) }
