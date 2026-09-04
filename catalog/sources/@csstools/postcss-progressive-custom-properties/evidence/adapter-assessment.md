# Adapter Assessment

The package is a PostCSS plugin rather than a standalone CLI. A separate
verifier must invoke the candidate through a child-side JSON adapter that owns
the PostCSS parser, processor, result serialization, and bounded input/output
limits. The trusted verifier must not import candidate modules directly.

The package has an ESM default export plus a `module.exports` compatibility
export, depends on `postcss-value-parser`, and requires a PostCSS 8 peer. The
upstream test harness additionally depends on `@csstools/postcss-tape` and
`@webref/css`; the complete exact npm closure was not available in the offline
image. A bounded offline `npm ci --offline --ignore-scripts` probe failed with
`ENOTCACHED` for `zod@4.4.3` before tests could be collected.

The source-only fixtures are CSS files, and their expected output is a public
behavior contract. No fixed leaf denominator was claimed because the harness
was not executable under the available closure. No Oracle, controls, reward,
or generated runtime is claimed.
