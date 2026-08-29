import {spawnSync} from 'node:child_process'

const NODE = process.env.NODE_BINARY ?? process.execPath
const MAX_REQUEST_BYTES = 128 * 1024
const MAX_RESPONSE_BYTES = 256 * 1024

const ADAPTER = String.raw`
import {join} from 'node:path'
import {pathToFileURL} from 'node:url'

const {toJsxRuntime} = await import(pathToFileURL(join(process.cwd(), 'node_modules/hast-util-to-jsx-runtime/index.js')).href)

function emit(payload, code = 0) {
  process.stdout.write(JSON.stringify(payload) + '\n')
  process.exit(code)
}

function fail(message) {
  throw new TypeError(message)
}

function plainObject(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(label + ' must be an object')
  return value
}

function evaluateNode(node, bindings) {
  plainObject(node, 'expression')
  if (node.type === 'Literal') return node.value
  if (node.type === 'Identifier') return bindings[node.name]
  if (node.type === 'ArrayExpression') return node.elements.map((item) => evaluateNode(item, bindings))
  if (node.type === 'ObjectExpression') {
    return Object.fromEntries(node.properties.map((property) => [property.key.name ?? property.key.value, evaluateNode(property.value, bindings)]))
  }
  if (node.type === 'MemberExpression') {
    const object = evaluateNode(node.object, bindings)
    const key = node.computed ? evaluateNode(node.property, bindings) : node.property.name
    return object?.[key]
  }
  if (node.type === 'BinaryExpression') {
    const left = evaluateNode(node.left, bindings)
    const right = evaluateNode(node.right, bindings)
    if (node.operator === '+') return left + right
    if (node.operator === '===') return left === right
  }
  fail('unsupported test expression: ' + node.type)
}

function runtimeFor(request) {
  const options = {...(request.options ?? {})}
  const element = (type, props, key) => {
    const result = {type, props}
    if (key !== undefined) result.key = key
    return result
  }
  options.Fragment = 'Fragment'
  if (options.components) {
    options.components = Object.fromEntries(Object.entries(options.components).map(([name, value]) => [name, {name: value}]))
  }
  options.jsx = (type, props, key) => element(type, props, key)
  options.jsxs = (type, props, key) => element(type, props, key)
  if (request.mode === 'development') {
    options.development = true
    options.jsxDEV = (type, props, key, isStaticChildren, source) => ({
      ...element(type, props, key),
      dev: {isStaticChildren, source}
    })
  }
  if (request.bindings) {
    const bindings = request.bindings
    options.createEvaluater = () => ({
      evaluateExpression: (expression) => evaluateNode(expression, bindings),
      evaluateProgram: (program) => {
        const statement = program.body?.[0]
        return evaluateNode(statement?.expression ?? statement, bindings)
      }
    })
  }
  for (const name of request.omit ?? []) delete options[name]
  return options
}

try {
  const request = JSON.parse(process.env.HAST_REQUEST_JSON ?? 'null')
  plainObject(request, 'request')
  if (typeof request.id !== 'string' || request.id.length < 1 || request.id.length > 128) fail('request id is invalid')
  if (request.operation !== 'transform') fail('operation is invalid')
  const data = toJsxRuntime(request.tree, runtimeFor(request))
  emit({id: request.id, success: true, data})
} catch (error) {
  emit({success: false, boundaryError: true, errorType: error?.constructor?.name ?? 'Error', message: String(error?.message ?? error).slice(0, 1024)}, 1)
}
`

export function callCandidate(request) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const encoded = JSON.stringify(request)
  if (Buffer.byteLength(encoded) > MAX_REQUEST_BYTES) throw new Error('candidate request exceeds bound')
  const result = spawnSync(
    '/usr/bin/timeout',
    [
      '--signal=TERM',
      '--kill-after=5s',
      '30s',
      'runuser',
      '-u',
      'candidate',
      '--',
      '/usr/bin/prlimit',
      '--cpu=60',
      '--nproc=4096',
      '--nofile=128',
      '--',
      'env',
      '-i',
      'PATH=/usr/local/bin:/usr/bin:/bin',
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      `HAST_REQUEST_JSON=${encoded}`,
      NODE,
      '--no-addons',
      '--input-type=module',
      '--eval',
      ADAPTER
    ],
    {cwd: site, encoding: 'utf8', maxBuffer: MAX_RESPONSE_BYTES, timeout: 30_000}
  )
  if (result.error) throw result.error
  let payload
  try {
    payload = JSON.parse(result.stdout)
  } catch {
    throw new Error(`candidate response malformed (status=${result.status}): ${result.stdout}; stderr=${result.stderr}`)
  }
  if (result.status !== 0 || payload.boundaryError) {
    throw new Error(`candidate-call-failed: ${payload.message ?? result.stderr}`)
  }
  return payload
}
