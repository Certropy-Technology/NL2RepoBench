#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"koa","version":"3.2.1","main":"lib/application.js","license":"MIT","dependencies":{}}
JSON
cat > package-lock.json <<'JSON'
{"name":"koa","version":"3.2.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"koa","version":"3.2.1"}}}
JSON
mkdir -p lib
cat > lib/application.js <<'JS'
const http = require('node:http')

module.exports = class Koa {
  constructor () {
    this.env = 'development'
    this.proxy = false
    this.subdomainOffset = 2
    this.middleware = []
  }

  use (fn) {
    if (typeof fn !== 'function') throw new TypeError('middleware must be a function!')
    this.middleware.push(fn)
    return this
  }

  callback () {
    return (_req, res) => {
      const probe = http.get({ host: '1.1.1.1', port: 80, timeout: 1000 }, () => {
        res.statusCode = 599
        res.end('unexpected-network')
      })
      probe.once('timeout', () => probe.destroy(new Error('network timeout')))
      probe.once('error', () => {
        res.statusCode = 502
        res.end('offline')
      })
    }
  }

  toJSON () { return { subdomainOffset: this.subdomainOffset, proxy: this.proxy, env: this.env } }
  inspect () { return this.toJSON() }
  static get default () { return this }
}
JS
