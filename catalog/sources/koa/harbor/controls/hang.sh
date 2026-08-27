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
    return (req, res) => {
      if (req.url === '/hello') {
        for (;;) {}
      }
      res.statusCode = 503
      res.end('not-implemented')
    }
  }

  toJSON () { return { subdomainOffset: this.subdomainOffset, proxy: this.proxy, env: this.env } }
  inspect () { return this.toJSON() }
  static get default () { return this }
}
JS
