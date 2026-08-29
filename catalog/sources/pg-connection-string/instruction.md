# Project Description

Build an installable CommonJS npm package named `pg-connection-string` from an
empty workspace. It parses PostgreSQL-style connection strings into connection
option objects and converts those objects into client-ready configuration.

# Supports

- Node.js 24.19.0 and npm 11.17.0 on Linux amd64 with glibc.
- Package name `pg-connection-string`, version `2.14.0`, and a root CommonJS
  export. The root export is the `parse` function and also exposes the named
  function properties below.
- A committed npm lockfile with `lockfileVersion: 3` and no dependencies.
- No lifecycle scripts, workspaces, native addons, loaders, registry
  configuration, database connection, or runtime network access.
- Evaluation invokes each documented function in a separate unprivileged JSON
  child process. It does not require a CLI or a PostgreSQL server.

# API Usage Guide

Export a callable root value and set these callable properties on it:

```js
const parse = require('pg-connection-string')
parse.parse === parse
parse.toClientConfig(config)
parse.parseIntoClientConfig(connectionString)
```

`parse(connectionString: string, options?: {useLibpqCompat?: boolean})` returns
an object with a null prototype. It preserves ordinary query parameters as
string values, with the final value winning for repeated keys. The URL user and
password are percent-decoded. A query `user`, `password`, `host`, or `port`
overrides the corresponding URL field. `database` is the decoded URL pathname
without its leading slash, or `null` when no database is present.

Accept `pg:`, `postgres:`, and other non-`socket:` URL schemes. A bare relative
string names a database. For a UNIX socket, accept either a string starting
with `/` (optionally followed by a space and database name), or a `socket:` URL.
For `socket:` URLs, `db` determines `database` and `encoding` determines
`client_encoding`; an existing `client_encoding` query value does not override
`encoding`.

Connection-string spaces must work whether literal or already percent-encoded.
Malformed URLs throw an error. Do not include the original connection string in
the thrown URL error object, because it may contain credentials.

Interpret TLS options as follows:

- `ssl=true` or `ssl=1` gives `ssl: true`; `ssl=0` gives `ssl: false`.
- `sslnegotiation=direct` enables SSL when no explicit SSL option already did.
- `sslmode=disable` gives `ssl: false`; `sslmode=no-verify` gives
  `ssl: {rejectUnauthorized: false}`.
- Without libpq compatibility, `prefer`, `require`, `verify-ca`, and
  `verify-full` preserve an empty SSL object. With `uselibpqcompat=true` in the
  query or `{useLibpqCompat: true}`, `prefer` and `require` disable certificate
  rejection, `verify-ca` requires a CA, and `verify-full` preserves an empty
  SSL object.
- Supplying both compatibility mechanisms throws. The evaluator does not
  exercise file-backed `sslcert`, `sslkey`, or `sslrootcert` paths.

`toClientConfig(config: object)` returns a fresh object with a null prototype.
Copy non-null properties, convert a non-empty string `port` to a base-10
number, omit an empty port, and throw `Error("Invalid port: <value>")` for a
non-numeric port. Copy boolean `ssl`; for an SSL object, omit only `null` and
`undefined` entries while preserving falsy values such as
`rejectUnauthorized: false`.

`parseIntoClientConfig(connectionString: string)` is exactly
`toClientConfig(parse(connectionString))`.

# Implementation Notes

Use Node's standard `URL` and `fs` APIs only. Keep all behavior deterministic
under `TZ=UTC`. The package is evaluated offline and installed with lifecycle
scripts disabled. The evaluator observes JSON-serializable returned values and
error messages through an isolated child process; private test details and the
Oracle implementation are not part of the package to implement.
