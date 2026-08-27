import assert from 'node:assert/strict'
import { chmodSync, mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import test from 'node:test'
import { callCandidate } from './test_client.mjs'

function envFixture() {
  const root = mkdtempSync(join(tmpdir(), 'vite-env-contract-'))
  chmodSync(root, 0o755)
  writeFileSync(
    join(root, '.env'),
    'VITE_BASE=/base\nVITE_EXPANDED=$VITE_BASE/app\nPRIVATE=hidden\nCUSTOM_ONE=one\n',
  )
  writeFileSync(join(root, '.env.local'), 'VITE_LOCAL=local\n')
  writeFileSync(
    join(root, '.env.production'),
    'VITE_BASE=/prod\nCUSTOM_TWO=two\n',
  )
  writeFileSync(join(root, '.env.production.local'), 'VITE_FINAL=final\n')
  return root
}

function workspaceFixture() {
  const root = mkdtempSync(join(tmpdir(), 'vite-workspace-contract-'))
  chmodSync(root, 0o755)
  mkdirSync(join(root, 'packages', 'app', 'src'), { recursive: true })
  writeFileSync(
    join(root, 'package.json'),
    JSON.stringify({ name: 'workspace', workspaces: ['packages/*'] }),
  )
  writeFileSync(
    join(root, 'packages', 'app', 'package.json'),
    JSON.stringify({ name: 'app' }),
  )
  return root
}

test('defineConfig returns a JSON object without changing its shape', () => {
  const config = { base: '/app/', nested: { enabled: true }, values: [1, 2] }
  assert.deepEqual(callCandidate('defineConfig', [config]), config)
})

test('normalizePath resolves relative dot segments and duplicate separators', () => {
  assert.equal(callCandidate('normalizePath', ['a/../b//c']), 'b/c')
})

test('normalizePath preserves an absolute POSIX root and trailing slash', () => {
  assert.equal(callCandidate('normalizePath', ['/a/./b/../c/']), '/a/c/')
})

test('isCSSRequest accepts supported stylesheet extensions and queries', () => {
  for (const request of ['src/a.css', 'x.less?direct', 'a.scss', 'a.postcss']) {
    assert.equal(callCandidate('isCSSRequest', [request]), true)
  }
})

test('isCSSRequest rejects scripts and CSS-like suffixes', () => {
  for (const request of ['src/a.js', 'src/a.css.js', 'src/css']) {
    assert.equal(callCandidate('isCSSRequest', [request]), false)
  }
})

test('mergeAlias gives later mixed-schema aliases priority', () => {
  const result = callCandidate('mergeAlias', [
    [{ find: 'old', replacement: '/old' }],
    { newer: '/new', last: '/last' },
  ])
  assert.deepEqual(result, [
    { find: 'newer', replacement: '/new' },
    { find: 'last', replacement: '/last' },
    { find: 'old', replacement: '/old' },
  ])
})

test('mergeAlias keeps object schema and lets the right side overwrite', () => {
  assert.deepEqual(
    callCandidate('mergeAlias', [
      { a: '/a', shared: '/old' },
      { b: '/b', shared: '/new' },
    ]),
    { a: '/a', b: '/b', shared: '/new' },
  )
})

test('mergeAlias strips paired trailing slashes in array entries', () => {
  assert.deepEqual(
    callCandidate('mergeAlias', [
      [{ find: 'old/', replacement: '/old/' }],
      [{ find: 'new/', replacement: '/new/' }],
    ]),
    [
      { find: 'new', replacement: '/new' },
      { find: 'old', replacement: '/old' },
    ],
  )
})

test('mergeConfig deeply merges objects and concatenates arrays', () => {
  assert.deepEqual(
    callCandidate('mergeConfig', [
      { nested: { left: 1 }, values: ['a'] },
      { nested: { right: 2 }, values: ['b', 'c'] },
    ]),
    { nested: { left: 1, right: 2 }, values: ['a', 'b', 'c'] },
  )
})

test('mergeConfig merges root input strings into an ordered array', () => {
  assert.deepEqual(
    callCandidate('mergeConfig', [
      { input: 'src/a.js' },
      { input: 'src/b.js' },
    ]),
    { input: ['src/a.js', 'src/b.js'] },
  )
})

test('mergeConfig merges root input records by entry name', () => {
  assert.deepEqual(
    callCandidate('mergeConfig', [
      { input: { a: 'src/a.js', shared: 'src/old.js' } },
      { input: { b: 'src/b.js', shared: 'src/new.js' } },
    ]),
    { input: { a: 'src/a.js', b: 'src/b.js', shared: 'src/new.js' } },
  )
})

test('mergeConfig overwrites nested input rather than applying root rules', () => {
  assert.deepEqual(
    callCandidate('mergeConfig', [
      { build: { input: 'src/a.js' } },
      { build: { input: 'src/b.js' } },
    ]),
    { build: { input: 'src/b.js' } },
  )
})

test('mergeConfig combines resolve aliases across schemas', () => {
  assert.deepEqual(
    callCandidate('mergeConfig', [
      { resolve: { alias: [{ find: 'old', replacement: '/old' }] } },
      { resolve: { alias: { newer: '/new' } } },
    ]),
    {
      resolve: {
        alias: [
          { find: 'newer', replacement: '/new' },
          { find: 'old', replacement: '/old' },
        ],
      },
    },
  )
})

test('mergeConfig ignores null and undefined-like JSON values', () => {
  assert.deepEqual(
    callCandidate('mergeConfig', [
      { base: '/old', nested: { keep: true } },
      { base: null, nested: null },
    ]),
    { base: '/old', nested: { keep: true } },
  )
})

test('mergeConfig preserves true for SSR external controls', () => {
  assert.deepEqual(
    callCandidate('mergeConfig', [
      { ssr: { noExternal: true, external: true } },
      { ssr: { noExternal: ['a'], external: ['b'] } },
    ]),
    { ssr: { noExternal: true, external: true } },
  )
})

test('mergeConfig treats environment resolve settings as root-like', () => {
  assert.deepEqual(
    callCandidate('mergeConfig', [
      { environments: { ssr: { resolve: { noExternal: true } } } },
      { environments: { ssr: { resolve: { noExternal: ['a'] } } } },
    ]),
    { environments: { ssr: { resolve: { noExternal: true } } } },
  )
})

test('resolveEnvPrefix supplies the VITE_ default', () => {
  assert.deepEqual(callCandidate('resolveEnvPrefix', [{}]), ['VITE_'])
})

test('resolveEnvPrefix preserves multiple valid prefixes in order', () => {
  assert.deepEqual(
    callCandidate('resolveEnvPrefix', [{ envPrefix: ['VITE_', 'PUBLIC_'] }]),
    ['VITE_', 'PUBLIC_'],
  )
})

test('resolveEnvPrefix rejects an empty prefix', () => {
  assert.throws(
    () => callCandidate('resolveEnvPrefix', [{ envPrefix: '' }]),
    /candidate-call-failed.*unexpected exposure/,
  )
})

test('sortUserPlugins groups pre normal and post plugins stably', () => {
  const plugins = [
    [{ name: 'normal-a' }, { name: 'pre', enforce: 'pre' }],
    { name: 'post', enforce: 'post' },
    { name: 'normal-b' },
  ]
  assert.deepEqual(callCandidate('sortUserPlugins', [plugins]), [
    [{ name: 'pre', enforce: 'pre' }],
    [{ name: 'normal-a' }, { name: 'normal-b' }],
    [{ name: 'post', enforce: 'post' }],
  ])
})

test('loadEnv applies file precedence expansion and VITE_ filtering', () => {
  const root = envFixture()
  try {
    assert.deepEqual(callCandidate('loadEnv', ['production', root]), {
      VITE_BASE: '/prod',
      VITE_EXPANDED: '/prod/app',
      VITE_LOCAL: 'local',
      VITE_FINAL: 'final',
    })
  } finally {
    rmSync(root, { recursive: true, force: true })
  }
})

test('loadEnv accepts an ordered array of custom prefixes', () => {
  const root = envFixture()
  try {
    assert.deepEqual(
      callCandidate('loadEnv', ['production', root, ['CUSTOM_']]),
      { CUSTOM_ONE: 'one', CUSTOM_TWO: 'two' },
    )
  } finally {
    rmSync(root, { recursive: true, force: true })
  }
})

test('loadEnv rejects local as a mode name', () => {
  const root = envFixture()
  try {
    assert.throws(
      () => callCandidate('loadEnv', ['local', root]),
      /candidate-call-failed.*cannot be used as a mode name/,
    )
  } finally {
    rmSync(root, { recursive: true, force: true })
  }
})

test('searchForWorkspaceRoot finds the nearest workspace marker above a package', () => {
  const root = workspaceFixture()
  try {
    assert.equal(
      callCandidate('searchForWorkspaceRoot', [
        join(root, 'packages', 'app', 'src'),
      ]),
      root,
    )
  } finally {
    rmSync(root, { recursive: true, force: true })
  }
})
