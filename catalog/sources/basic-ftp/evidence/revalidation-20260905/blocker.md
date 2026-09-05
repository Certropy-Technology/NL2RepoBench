# Instruction Revalidation Blocker

- Task: `basic-ftp`
- Revalidation date: 2026-09-05
- Expected current source content digest: `sha256:e9d1d2d8078d86cb7365f857759a55f86ea489d841db38318ac6644dbfc6abe6`
- Source validation: passed with `uv run nl2repo task validate-source catalog/sources/basic-ftp`.
- Lifecycle: unchanged at `controls-passed`; this is not a lifecycle transition.

## Compile evidence

The current source was compiled twice with the Node/npm locked toolchain, the parent
private CAS, and `--allow-private`:

```text
uv run nl2repo harbor compile catalog/sources/basic-ftp --output .nl2repo/basic-ftp-revalidation-compile-a --toolchain toolchain.node.lock.toml --artifact-root <parent-private-CAS> --allow-private
uv run nl2repo harbor compile catalog/sources/basic-ftp --output .nl2repo/basic-ftp-revalidation-compile-b --toolchain toolchain.node.lock.toml --artifact-root <parent-private-CAS> --allow-private
diff -rq .nl2repo/basic-ftp-revalidation-compile-a/basic-ftp .nl2repo/basic-ftp-revalidation-compile-b/basic-ftp
```

Both commands exited `0`; the output trees were byte-identical. Both bundle manifests
have file SHA-256 `sha256:6ee7541d205ece259061dacc1289a36e61f36b92945a415c8000bf12c8a2a593`,
canonical manifest digest `sha256:c24441a56bc61a39d93df48c037af48f070295fa139714add646ec6e008c4d5d`,
and 110 files.

## Blocker

The compiled Oracle contains `solution/fetch-source.mjs`, which performs an HTTPS GET to
`https://codeload.github.com/patrickjuchli/basic-ftp/tar.gz/9cbc5cf23cb2b62231bc1822a868138e4772d4e5`.
`solution/solve.sh` invokes that fetch before verifying the archive digest. This violates
the revalidation NoNetwork contract, so Harbor Oracle and controls were not run and no
current Oracle/control result is claimed. The historical `production-evidence.json` was
left unchanged because its old receipt paths are not durable current evidence.

## Remediation

Register a local Oracle bundle containing the exact frozen source payload, or replace the
network fetch with a source-local immutable payload whose archive bytes verify to
`sha256:515fbf4bfc6fed25ed9b58d5ef72d9d67cbe13cb4a2b6ca5abdcff4435ae092e`. The replacement
must be registered in private CAS, compiled into a new bundle, and followed by a complete
NoNetwork Oracle, empty, stub, forgery, and offline matrix. Until then this task remains
pending revalidation rather than controls-passed for the migrated instruction.
