# go-cron instruction revalidation blocker

The migrated instruction source digest is `sha256:076475cbe1531bbbf2765596e8335b2b36945c029d790b959c2ebfbae1e5a36f`, and the frozen upstream revision/source digest remain `bc59245fe10efaed9d51b56900192527ed733435` / `sha256:0cedb5d66d073dc2201d192e0ca89c11b722134a03d9323134280ec647570139`.

All three declared private CAS objects were found and verified by size and SHA-256. Two fresh Harbor 0.21.0 Go compiles using `toolchain.go.lock.toml`, `--allow-private`, and no `--allow-incomplete` produced byte-identical 68-file bundles. Their manifest file hash is `sha256:340ac42cf172e2bce8fbe8f46c733c0d79f82ee098fe3efec55c20a65fe4fc4a` and canonical manifest digest is `sha256:7dd8e3c0af7e2372c253948264625de9e6c902af0dfb9884a8a81f5598475c48`.

The frozen Oracle CAS object contains only `solve.sh`. It initializes a temporary git repository, fetches the pinned revision from `github.com`, creates the source archive, and checks its digest. This violates the required NoNetwork policy. The current Oracle bundle, task-local evidence, historical handoffs and authoring state, compiled trees, and local source archive inventory were searched. No source/module payload matching the frozen revision and declared digest was found, so no replacement private bundle can be proposed.

Oracle and controls were intentionally not run, and no historical receipt was reused. Lifecycle and `production-evidence.json` remain unchanged. The parent must provide/register a matching local-only Oracle payload before rerunning the final Oracle and controls matrix.
