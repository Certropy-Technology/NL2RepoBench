import {spawnSync} from 'node:child_process'

const code = `
const request = JSON.parse(process.env.VFM_REQUEST)
const mod = await import('vfile-message')
if (request.mode === 'surface') {
  process.stdout.write(JSON.stringify({ok: true, value: {exports: Object.keys(mod).sort(), isClass: /^class\\s/.test(Function.prototype.toString.call(mod.VFileMessage))}}) + '\\n')
  process.exit(0)
}
const before = JSON.stringify(request)
let first = request.reason
if (request.cause) {
  first = new Error(request.cause.message)
  first.name = request.cause.name || 'Error'
  first.stack = first.name + ': ' + first.message + '\\n    at synthetic'
}
let second = request.second
if (second && second.cause && typeof second.cause.message === 'string') {
  const cause = new Error(second.cause.message)
  cause.name = second.cause.name || 'Error'
  cause.stack = cause.name + ': ' + cause.message + '\\n    at synthetic'
  second = {...second, cause}
}
const args = [first]
if (Object.prototype.hasOwnProperty.call(request, 'second')) args.push(second)
if (Object.prototype.hasOwnProperty.call(request, 'origin')) args.push(request.origin)
const message = new mod.VFileMessage(...args)
const value = {
  isError: message instanceof Error,
  name: message.name,
  message: message.message,
  reason: message.reason,
  file: message.file,
  fatal: message.fatal,
  line: message.line,
  column: message.column,
  place: message.place,
  ruleId: message.ruleId,
  source: message.source,
  stackFirst: typeof message.stack === 'string' ? message.stack.split('\\n')[0] : message.stack,
  string: String(message),
  ancestorsLength: Array.isArray(message.ancestors) ? message.ancestors.length : undefined,
  cause: message.cause ? {name: message.cause.name, message: message.cause.message} : undefined,
  actual: message.actual,
  expected: message.expected,
  note: message.note,
  url: message.url,
  inputUnchanged: JSON.stringify(request) === before
}
process.stdout.write(JSON.stringify({ok: true, value}) + '\\n')
`

export function surface() {
  return invoke({mode: 'surface'})
}

export function construct(request) {
  return invoke(request)
}

function invoke(request) {
  const result = spawnSync('/usr/bin/timeout', ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--', '/usr/bin/prlimit', '--cpu=60', '--nproc=32', '--nofile=128', '--', 'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', 'HOME=/tmp/candidate-home', 'TMPDIR=/tmp/candidate-tmp', 'NODE_ALLOWED_PACKAGE=vfile-message', `VFM_REQUEST=${JSON.stringify(request)}`, '/usr/local/bin/node', '--no-addons', '--input-type=module', '-e', code], {cwd: process.env.NODE_CANDIDATE_SITE, env: process.env, encoding: 'utf8', timeout: 30000, maxBuffer: 256 * 1024})
  if (result.error) throw result.error
  let payload
  try { payload = JSON.parse(result.stdout) } catch { throw new Error('candidate response malformed: ' + result.stdout) }
  if (!payload.ok) throw new Error(payload.error || 'candidate-call-failed')
  return payload.value
}
