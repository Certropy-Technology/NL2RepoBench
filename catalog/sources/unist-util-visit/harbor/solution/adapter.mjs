import {readFileSync} from 'node:fs'
import {CONTINUE, EXIT, SKIP, visit} from './index.js'

const request = JSON.parse(readFileSync(0, 'utf8'))
const tree = structuredClone(request.tree)
const visits = []
let calls = 0
let restartCount = 0
let restarted = false
const predicate = typeof request.predicateIndexAtLeast === 'number'
  ? (_node, index) => typeof index === 'number' && index >= request.predicateIndexAtLeast
  : undefined
const test = predicate ?? request.test
const visitor = (node, index, parent) => {
  calls += 1
  const record = {type: node.type}
  if (typeof index === 'number') record.index = index
  if (parent && typeof parent.type === 'string') record.parentType = parent.type
  visits.push(record)
  if (request.markVisited) node.marked = true
  if (typeof request.exitAfter === 'number' && calls >= request.exitAfter) return EXIT
  if (request.skipType === node.type) return SKIP
  if (request.restartOnceType === node.type && !restarted) {
    restarted = true
    restartCount += 1
    return 0
  }
  if (request.jumpAtType === node.type) return [CONTINUE, request.jumpIndex]
  if (request.mode === 'undefined') return undefined
  return CONTINUE
}

const reverse = request.reverse === true
if (test === undefined) visit(tree, visitor, reverse)
else visit(tree, test, visitor, reverse)
process.stdout.write(`${JSON.stringify({ok: true, exports: ['CONTINUE', 'EXIT', 'SKIP'], visits, calls, restartCount, tree})}\n`)
