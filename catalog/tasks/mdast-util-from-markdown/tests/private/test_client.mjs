import {spawnSync} from 'node:child_process'

// Keep the trusted bridge in this root-only test file. The candidate UID must
// not need read access to the private test directory or be able to rewrite the
// adapter before the child process imports the candidate package.
const adapterCode = `
import {readFileSync} from 'node:fs'
import {join} from 'node:path'
import {pathToFileURL} from 'node:url'

const request = JSON.parse(readFileSync(0, 'utf8'))
const candidateRoot = join(process.env.NODE_CANDIDATE_SITE ?? process.cwd(), 'node_modules', 'mdast-util-from-markdown')
const {fromMarkdown} = await import(pathToFileURL(join(candidateRoot, 'index.js')).href)

function stripPositions(value) {
  if (Array.isArray(value)) return value.map(stripPositions)
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value)
        .filter(([key]) => key !== 'position')
        .map(([key, nested]) => [key, stripPositions(nested)])
    )
  }
  return value
}

function respond(value) {
  process.stdout.write(JSON.stringify({id: request.id, ok: true, value}) + '\\n')
}

try {
  if (request.operation === 'inventory') {
    const manifest = JSON.parse(readFileSync(join(candidateRoot, 'package.json'), 'utf8'))
    const module = await import(pathToFileURL(join(candidateRoot, 'index.js')).href)
    respond({
      packageName: manifest.name,
      packageVersion: manifest.version,
      packageShape: manifest.type === 'module' && manifest.files?.includes('index.js'),
      runtimeEntry: typeof module.fromMarkdown === 'function',
      declarationEntry: manifest.files?.includes('index.d.ts') === true,
      exportNames: Object.keys(module).sort()
    })
  } else if (request.operation === 'parse' || request.operation === 'parse-positions') {
    if (typeof request.input !== 'string') throw new TypeError('input must be a string')
    const tree = fromMarkdown(request.input)
    respond(request.operation === 'parse' ? stripPositions(tree) : tree)
  } else {
    throw new Error('unknown adapter operation')
  }
} catch (error) {
  process.stdout.write(JSON.stringify({
    id: request.id,
    ok: false,
    error: error?.constructor?.name ?? 'Error',
    message: String(error?.message ?? error)
  }) + '\\n')
  process.exitCode = 1
}
`
let sequence = 0

export function call(operation, input) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const id = `request-${++sequence}`
  const payload = JSON.stringify({id, operation, input})
  if (Buffer.byteLength(payload) > 64 * 1024) throw new Error('request is too large')
  const result = spawnSync(
    '/usr/bin/timeout',
    ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
      '/usr/bin/prlimit', '--cpu=30', '--nproc=64', '--nofile=128', '--',
      'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`, `NODE_CANDIDATE_SITE=${site}`, 'TERM=dumb', 'CI=true', 'LC_ALL=C.UTF-8',
      'NODE_ALLOWED_PACKAGE=mdast-util-from-markdown',
      '/usr/local/bin/node', '--no-addons', '--input-type=module', '--eval', adapterCode],
    {cwd: site, input: `${payload}\n`, encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000}
  )
  if (result.error || result.status !== 0 || !result.stdout) {
    throw new Error(`candidate child failed: ${result.stderr || result.error || result.status}`)
  }
  let response
  try {
    response = JSON.parse(result.stdout)
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`)
  }
  if (response.id !== id) throw new Error('candidate response id mismatch')
  if (Buffer.byteLength(JSON.stringify(response)) > 256 * 1024) throw new Error('response too large')
  return response
}

export function parse(input) {
  const response = call('parse', input)
  if (!response.ok) throw new Error(response.message)
  return response.value
}

export function parsePositions(input) {
  const response = call('parse-positions', input)
  if (!response.ok) throw new Error(response.message)
  return response.value
}

export function inventory() {
  const response = call('inventory')
  if (!response.ok) throw new Error(response.message)
  return response.value
}
