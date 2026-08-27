import { spawnSync } from 'node:child_process'

const RUNNER = '/tests/runtime/node/candidate_runner.mjs'
const NODE = '/usr/local/bin/node'

function invoke(packageName, exportName, args) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
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
      '--nproc=32',
      '--nofile=128',
      '--',
      'env',
      '-i',
      'PATH=/usr/local/bin:/usr/bin:/bin',
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      `NODE_ALLOWED_PACKAGE=${packageName}`,
      NODE,
      '--no-addons',
      RUNNER,
    ],
    {
      cwd: site,
      input: `${JSON.stringify({ package: packageName, export: exportName, args })}\n`,
      encoding: 'utf8',
      maxBuffer: 256 * 1024,
      timeout: 30_000,
    },
  )
  if (result.error) throw result.error
  let payload
  try {
    payload = JSON.parse(result.stdout)
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`)
  }
  return payload
}

export function callCandidate(exportName, args, packageName = 'nanoid') {
  const payload = invoke(packageName, exportName, args)
  if (!payload.ok) {
    const error = new Error(payload.message ?? payload.error ?? 'candidate-call-failed')
    error.exceptionType = payload.exception_type
    throw error
  }
  return payload.value
}

export function callCandidateStatus(exportName, args, packageName = 'nanoid') {
  return invoke(packageName, exportName, args)
}

export function callFactory(
  exportName,
  packageName,
  factoryArgs,
  callArgs,
  randomSequence,
) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const script = `
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import { readFileSync } from 'node:fs'
const request = JSON.parse(readFileSync(0, 'utf8'))
const require = createRequire(pathToFileURL(\`${'${process.cwd()}'}/package.json\`))
let candidate
try { candidate = require(request.package) } catch (error) {
  if (error?.code !== 'ERR_REQUIRE_ESM' && error?.code !== 'ERR_PACKAGE_PATH_NOT_EXPORTED') throw error
  const root = \`${'${process.cwd()}'}/node_modules/\${request.package}\`
  const manifest = JSON.parse(readFileSync(\`${'${root}'}/package.json\`, 'utf8'))
  const entry = manifest.exports?.['.']?.import ?? manifest.exports?.['.']?.default ?? manifest.module ?? manifest.main
  candidate = await import(pathToFileURL(\`${'${root}'}/\${entry.slice(2)}\`).href)
}
const random = request.randomSequence ? size => {
  const bytes = []
  for (let i = 0; i < size; i++) bytes.push(request.randomSequence[i % request.randomSequence.length])
  return Uint8Array.from(bytes)
} : undefined
const args = [...request.factoryArgs]
if (random) args.push(random)
const value = candidate[request.export](...args)(...request.callArgs)
process.stdout.write(JSON.stringify({ ok: true, value }) + '\\n')
`
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
      '--nproc=32',
      '--nofile=128',
      '--',
      'env',
      '-i',
      'PATH=/usr/local/bin:/usr/bin:/bin',
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      `NODE_ALLOWED_PACKAGE=${packageName}`,
      NODE,
      '--no-addons',
      '--input-type=module',
      '--eval',
      script,
    ],
    {
      cwd: site,
      input: `${JSON.stringify({ package: packageName, export: exportName, factoryArgs, callArgs, randomSequence })}\n`,
      encoding: 'utf8',
      maxBuffer: 256 * 1024,
      timeout: 30_000,
    },
  )
  if (result.error) throw result.error
  let payload
  try {
    payload = JSON.parse(result.stdout)
  } catch {
    throw new Error(`factory response malformed: ${result.stdout}`)
  }
  if (!payload.ok) throw new Error(payload.message ?? payload.error ?? 'factory-call-failed')
  return payload.value
}

export function callFactorySequence(
  exportName,
  packageName,
  factoryArgs,
  callArgsSequence,
) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const script = `
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import { readFileSync } from 'node:fs'
const request = JSON.parse(readFileSync(0, 'utf8'))
const require = createRequire(pathToFileURL(\`${'${process.cwd()}'}/package.json\`))
let candidate
try { candidate = require(request.package) } catch (error) {
  if (error?.code !== 'ERR_REQUIRE_ESM' && error?.code !== 'ERR_PACKAGE_PATH_NOT_EXPORTED') throw error
  const root = \`${'${process.cwd()}'}/node_modules/\${request.package}\`
  const manifest = JSON.parse(readFileSync(\`${'${root}'}/package.json\`, 'utf8'))
  const entry = manifest.exports?.['.']?.import ?? manifest.exports?.['.']?.default ?? manifest.module ?? manifest.main
  candidate = await import(pathToFileURL(\`${'${root}'}/\${entry.slice(2)}\`).href)
}
const factory = candidate[request.export](...request.factoryArgs)
const value = request.callArgsSequence.map(args => factory(...args))
process.stdout.write(JSON.stringify({ ok: true, value }) + '\\n')
`
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
      '--nproc=32',
      '--nofile=128',
      '--',
      'env',
      '-i',
      'PATH=/usr/local/bin:/usr/bin:/bin',
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      NODE,
      '--no-addons',
      '--input-type=module',
      '--eval',
      script,
    ],
    {
      cwd: site,
      input: `${JSON.stringify({ package: packageName, export: exportName, factoryArgs, callArgsSequence })}\n`,
      encoding: 'utf8',
      maxBuffer: 256 * 1024,
      timeout: 30_000,
    },
  )
  if (result.error) throw result.error
  let payload
  try {
    payload = JSON.parse(result.stdout)
  } catch {
    throw new Error(`factory sequence response malformed: ${result.stdout}`)
  }
  if (!payload.ok) throw new Error(payload.message ?? payload.error ?? 'factory-sequence-failed')
  return payload.value
}

export function readCandidateExport(exportName, packageName = 'nanoid') {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const script = `
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import { readFileSync } from 'node:fs'
const request = JSON.parse(readFileSync(0, 'utf8'))
const require = createRequire(pathToFileURL(\`${'${process.cwd()}'}/package.json\`))
let candidate
try { candidate = require(request.package) } catch (error) {
  if (error?.code !== 'ERR_REQUIRE_ESM' && error?.code !== 'ERR_PACKAGE_PATH_NOT_EXPORTED') throw error
  const root = \`${'${process.cwd()}'}/node_modules/\${request.package}\`
  const manifest = JSON.parse(readFileSync(\`${'${root}'}/package.json\`, 'utf8'))
  const entry = manifest.exports?.['.']?.import ?? manifest.exports?.['.']?.default ?? manifest.module ?? manifest.main
  candidate = await import(pathToFileURL(\`${'${root}'}/\${entry.slice(2)}\`).href)
}
process.stdout.write(JSON.stringify({ ok: true, value: candidate[request.export] }) + '\\n')
`
  const result = spawnSync(
    '/usr/bin/timeout',
    ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--', '/usr/bin/prlimit', '--cpu=60', '--nproc=32', '--nofile=128', '--', 'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`, `NODE_ALLOWED_PACKAGE=${packageName}`, NODE, '--no-addons', '--input-type=module', '--eval', script],
    { cwd: site, input: `${JSON.stringify({ package: packageName, export: exportName })}\n`, encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 30_000 },
  )
  if (result.error) throw result.error
  const payload = JSON.parse(result.stdout)
  if (!payload.ok) throw new Error(payload.error ?? 'candidate-export-failed')
  return payload.value
}

export function runCli(args) {
  const site = process.env.NODE_CANDIDATE_SITE
  if (!site) throw new Error('candidate site is not configured')
  const bin = `${site}/node_modules/nanoid/bin/nanoid.js`
  return spawnSync(
    'runuser',
    [
      '-u',
      'candidate',
      '--',
      'env',
      '-i',
      'PATH=/usr/local/bin:/usr/bin:/bin',
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      '/usr/local/bin/node',
      bin,
      ...args,
    ],
    { cwd: site, encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 30_000 },
  )
}
