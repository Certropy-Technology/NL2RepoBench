# Authoring Provenance

The source was frozen from `https://github.com/sindresorhus/parse-json` at
commit `6fee59751db59a539fdf53537101a1d7c6378a65`. The raw Git archive digest
is recorded in `task.toml`; the MIT license bytes were checked separately.

The upstream package has no committed lockfile. Authoring remediation resolved
its exact runtime ranges to an npm v3 lock and private cache closure containing
`@babel/code-frame@7.29.7`, `@babel/helper-validator-identifier@7.29.7`,
`js-tokens@4.0.0`, `picocolors@1.1.1`, `index-to-position@1.2.0`, and
`type-fest@4.41.0`. The resulting npm v3 lock has SHA-256
`e4d8b372661c034be2b58e9129b463477fa9d65a56709733ebc34bdc8d3489ee`.
Development-only AVA/XO/tsd dependencies are not part of the candidate runtime.
The private test and Oracle bundles are stored under the task-local
content-addressed artifact root and are never copied to the public source.
