# go-cmp instruction revalidation blocker

The migrated instruction remains factually consistent with the task-local API inventory,
traceability map, frozen bridge, and Go module metadata. No instruction edit was needed.

The expected catalog digest `sha256:58390d2ae77c9595b8293140ab9bf59b46b168f20ac17d9eedefefdb623c2dc0`
and all three private CAS objects were verified. Two production compiles with
`toolchain.go.lock.toml` and `--allow-private` were byte-identical: 67 files, manifest
`sha256:e5586d325fe5b6d12a6cea86a7365f1427c91793eb783482238798f98df4887a`, canonical manifest
`sha256:5f17202bed13788349a27106bd1601176e5921fe6f0b694c83a46606edf4a807`.

The Oracle bundle contains only `solve.sh` and performs a runtime `git fetch` from
`github.com`. Under the required NoNetwork contract, Oracle and controls were not run.
The bounded local search found no source archive or replacement payload whose bytes could
be verified against revision `b133f1f1932e48f466f597a3346ce6f5a49a0dc1` and source archive
digest `sha256:0db58f99e9ff0c467df202b87cd72b97b8518b01ada824b8d9259e6a09b017fe`.

Failure class: `artifact-or-verifier-blocked`.

Next step: parent registers a trusted, locally supplied Oracle source payload only after
verifying its revision and archive digest, then recompiles and runs the complete Oracle and
controls matrix against the new final manifest. No lifecycle, production evidence, or
generated projection was changed by this revalidation.
