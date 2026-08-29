import packageJson from './package.json' with {type: 'json'}
import {mdxjsEsmFromMarkdown, mdxjsEsmToMarkdown} from './index.js'

function object(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`${label} must be an object`)
  }
  return value
}

export async function run(request) {
  object(request, 'request')
  if (typeof request.op !== 'string') throw new Error('op must be a string')

  if (request.op === 'api') {
    const from = mdxjsEsmFromMarkdown()
    const to = mdxjsEsmToMarkdown()
    return {
      name: packageJson.name,
      version: packageJson.version,
      exports: ['mdxjsEsmFromMarkdown', 'mdxjsEsmToMarkdown'],
      from: {enter: Object.keys(from.enter).sort(), exit: Object.keys(from.exit).sort()},
      to: {handlers: Object.keys(to.handlers).sort()}
    }
  }

  if (request.op === 'from-enter') {
    const token = object(request.token ?? {}, 'token')
    const extension = mdxjsEsmFromMarkdown()
    const calls = []
    const context = {
      enter(node, receivedToken) { calls.push({kind: 'enter', node, token: receivedToken}) },
      buffer() { calls.push({kind: 'buffer'}) }
    }
    extension.enter.mdxjsEsm.call(context, token)
    return {calls}
  }

  if (request.op === 'from-exit') {
    const token = object(request.token ?? {}, 'token')
    const extension = mdxjsEsmFromMarkdown()
    const node = {type: request.stackType ?? 'mdxjsEsm', value: 'old'}
    const calls = []
    const context = {
      stack: [node],
      resume() { calls.push({kind: 'resume'}); return request.value },
      exit(receivedToken) { calls.push({kind: 'exit', token: receivedToken}) }
    }
    if (Object.hasOwn(request, 'estree')) token.estree = request.estree
    extension.exit.mdxjsEsm.call(context, token)
    return {node, calls}
  }

  if (request.op === 'from-data') {
    const token = object(request.token ?? {}, 'token')
    const events = []
    const context = {
      config: {
        enter: {data(receivedToken) { events.push({kind: 'enter', token: receivedToken}) }},
        exit: {data(receivedToken) { events.push({kind: 'exit', token: receivedToken}) }}
      }
    }
    const extension = mdxjsEsmFromMarkdown()
    extension.exit.mdxjsEsmData.call(context, token)
    return {events}
  }

  if (request.op === 'to-markdown') {
    const node = object(request.node ?? {}, 'node')
    return {value: mdxjsEsmToMarkdown().handlers.mdxjsEsm(node)}
  }

  if (request.op === 'factories') {
    const fromA = mdxjsEsmFromMarkdown()
    const fromB = mdxjsEsmFromMarkdown()
    const toA = mdxjsEsmToMarkdown()
    const toB = mdxjsEsmToMarkdown()
    return {fromIndependent: fromA !== fromB, toIndependent: toA !== toB, handlersShared: fromA.enter.mdxjsEsm === fromB.enter.mdxjsEsm && toA.handlers.mdxjsEsm === toB.handlers.mdxjsEsm}
  }

  throw new Error(`unsupported operation: ${request.op}`)
}
