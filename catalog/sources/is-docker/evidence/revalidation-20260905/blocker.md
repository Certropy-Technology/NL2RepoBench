# is-docker instruction revalidation blocker

The queued current source digest was `sha256:654e1596a2f8daa972fb91493bc4cf8eb36a67965972f4142c88cf400945317c`; `uv run nl2repo task validate-source catalog/sources/is-docker` passed with that digest.

All four declared private artifacts were present in the parent CAS and matched their declared sizes and SHA-256 values. The Oracle bundle is structurally valid as a 1,357-byte tar, but contains only `solve.sh`. That script performs a runtime fetch from `github.com`, which cannot be executed under this revalidation's NoNetwork contract.

The bounded local-recovery search covered the generated task projection, task-local evidence, retained authoring worktrees and handoffs, run receipts, and local npm cache. It found no bytes matching the required prefixed Git archive digest `sha256:4b0b0b2f7949858e2c44da8b3dd2224ccc95eb8545674c867147ae93e6381cb5`. The local npm cache does contain the `is-docker@4.0.0` release body: 1,779 bytes, SHA-1 `6aab87c77a30ddff39c460af372ee1795aee7848`, published SHA-512 integrity `sha512-LHE+wROyG/Y/0ZnbktRCoTix2c1RhgWaZraMZ8o1Q7zCh0VSrICJQO5oqIIISrcSBtrXv0o233w1IYwsWCjTzA==`, and `gitHead` `59379f14b6dda26a0167fce55d80bf546857f92d`. Its six npm package members are not the 13-file prefixed Git archive and cannot establish the required archive bytes.

Therefore no replacement bundle was constructed, and compile, Oracle, and controls were not run. Existing lifecycle `packaged` and `production-evidence.json` remain unchanged. The machine-readable command and hash audit is in `evidence/revalidation-20260905/recovery-search.json`.

Next unblock action: recover or provide a local source archive hashing to the declared `sha256:4b0b0b2f7949858e2c44da8b3dd2224ccc95eb8545674c867147ae93e6381cb5`, register a verified replacement Oracle bundle in the parent CAS, recompile, then run the complete NoNetwork Oracle/control matrix.
